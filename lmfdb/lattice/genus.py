
import re
import time

from flask import abort, render_template, request, url_for, redirect, make_response
from sage.all import ZZ, QQ, PolynomialRing, latex, matrix, PowerSeriesRing, sqrt, round

from lmfdb.utils import (
    web_latex_split_on_pm, flash_error, to_dict,
    SearchArray, TextBox, CountBox, prop_int_pretty,
    parse_ints, parse_list, parse_count, parse_start, clean_input,
    search_wrap, redirect_no_cache, Downloader)
from lmfdb.utils.interesting import interesting_knowls
from lmfdb.utils.search_columns import SearchColumns, LinkCol, MathCol
from lmfdb.api import datapage
from lmfdb.lattice import genus_page
from lmfdb.lattice.isom import isom
from lmfdb.lattice.genera_stats import Genus_stats

# Database connection

from lmfdb import db

# utilitary functions for displays


def vect_to_matrix(v):
    return str(latex(matrix(v)))


def print_q_expansion(lst):
    lst = [str(c) for c in lst]
    Qa = PolynomialRing(QQ, 'a')
    Qq = PowerSeriesRing(Qa, 'q')
    return web_latex_split_on_pm(Qq(lst).add_bigoh(len(lst)))


def my_latex(s):
    ss = ""
    ss += re.sub(r'x\d', 'x', s)
    ss = re.sub(r"\^(\d+)", r"^{\1}", ss)
    ss = re.sub(r'\*', '', ss)
    ss = re.sub(r'zeta(\d+)', r'zeta_{\1}', ss)
    ss = re.sub('zeta', r'\\zeta', ss)
    ss += ""
    return ss


# breadcrumbs and links for data quality entries

def get_bread(tail=[]):
    base = [("Genus", url_for(".genus_render_webpage"))]
    if not isinstance(tail, list):
        tail = [(tail, " ")]
    return base + tail


def learnmore_list():
    return [('Source and acknowledgments', url_for(".how_computed_page")),
            ('Completeness of the data', url_for(".completeness_page")),
            ('Reliability of the data', url_for(".reliability_page")),
            ('Labels for integral lattices', url_for(".labels_page")),
            ('History of lattices', url_for(".history_page"))]


# Return the learnmore list with the matchstring entry removed
def learnmore_list_remove(matchstring):
    return [t for t in learnmore_list() if t[0].find(matchstring) < 0]


# webpages: main, random and search results

@genus_page.route("/")
def genus_render_webpage():
    info = to_dict(request.args, search_array=GenusSearchArray())
    if not request.args:
        stats = Genus_stats()
        dim_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        #class_number_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 50, 51, 52, 54, 55, 56]
        # det_list_endpoints = [1, 1000, 10000, 100000, 1000000, 10000000, 100000000]
        det_list_endpoints = [1, 10, 100, 1000]
        det_list = ["%s-%s" % (start, end - 1) for start, end in zip(det_list_endpoints[:-1], det_list_endpoints[1:])]
        # name_list = ["A2", "Z2", "D3", "D3*", "3.1942.3884.56.1", "A5", "E8", "A14", "Leech"]
        info.update({'dim_list': dim_list, #'class_number_list': class_number_list,
                     'det_list': det_list, #'name_list': name_list
                     })
        t = 'Genera of integral lattices'
        bread = get_bread()
        info['stats'] = stats
        #info['max_cn'] = stats.max_cn
        info['max_rank'] = stats.max_rank
        info['max_det'] = stats.max_det
        return render_template("genus-index.html", info=info, title=t, learnmore=learnmore_list(), bread=bread)
    else:
        return genus_search(info)


# Random Lattice
@genus_page.route("/random")
@redirect_no_cache
def random_lattice():
    return url_for(".render_genus_webpage", label=db.lat_genera.random())


@genus_page.route("/interesting")
def interesting():
    return interesting_knowls(
        "genus",
        db.lat_genera,
        url_for_label=url_for_label,
        title=r"Some interesting genera of lattices",
        bread=get_bread("Interesting"),
        learnmore=learnmore_list()
    )


@genus_page.route("/stats")
def statistics():
    title = 'Genera of lattices: Statistics'
    bread = get_bread('Statistics')
    return render_template("display_stats.html", info=Genus_stats(), title=title, bread=bread, learnmore=learnmore_list())


lattice_label_regex = re.compile(r'(\d+)\.(\d+)\.(\d+)\.(\d+)\.(\d*)')


def split_genus_label(lab):
    return genus_label_regex.match(lab).groups()


def genus_by_label_or_name(lab):
    clean_lab = str(lab).replace(" ", "")
    clean_and_cap = str(clean_lab).capitalize()
    for l in [lab, clean_lab, clean_and_cap]:
        label = db.lat_genera.lucky(
            {'$or':
             [{'label': l}]},
            'label')
        if label is not None:
            return redirect(url_for(".render_genus_webpage", label=label))
    if genus_label_regex.match(lab):
        flash_error("The genus of integral lattices %s is not recorded in the database or the label is invalid", lab)
    else:
        flash_error("No integral lattice in the database has label or name %s", lab)
    return redirect(url_for(".genus_render_webpage"))


# download
download_comment_prefix = {'magma': '//', 'sage': '#', 'gp': '\\\\'}
download_assignment_start = {'magma': 'data := ', 'sage': 'data = ', 'gp': 'data = '}
download_assignment_end = {'magma': ';', 'sage': '', 'gp': ''}
download_file_suffix = {'magma': '.m', 'sage': '.sage', 'gp': '.gp'}


genus_search_projection = ['label', 'rank', 'det', 'level',
                             #'class_number', 'aut', 'minimum']
                           ]


def lattice_search_isometric(res, info, query):
    """
    We check for isometric lattices if the user enters a valid gram matrix
    but not one stored in the database

    This may become slow in the future: at the moment we compare against
    a list of stored matrices with same dimension and determinant
    (just compare with respect to dimension is slow)
    """
    if info['number'] == 0 and info.get('gram'):
        A = query['gram']
        n = len(A[0])
        d = matrix(A).determinant()
        for gram in db.lat_lattices.search({'dim': n, 'det': int(d)}, 'gram'):
            if isom(A, gram):
                query['gram'] = gram
                proj = lattice_search_projection
                count = parse_count(info)
                start = parse_start(info)
                res = db.lat_lattices.search(query, proj, limit=count, offset=start, info=info)
                break

    return res


def url_for_label(label):
    return url_for(".render_genus_webpage", label=label)


genus_columns = SearchColumns([
    LinkCol("label", "genus.label", "Label", url_for_label),
    MathCol("rank", "genus.rank", "Rank"),
    MathCol("signature", "genus.signature", "$n_+$"),
    MathCol("det", "genus.determinant", "Determinant"),
    MathCol("level", "genus.level", "Level"),
    # MathCol("class_number", "lattice.class_number", "Class number"),
    # MathCol("minimum", "lattice.minimal_vector", "Minimal vector"),
    #MathCol("aut", "lattice.group_order", "Aut. group order")
    ])


@search_wrap(table=db.lat_genera,
             title='Genera of integral lattices search results',
             err_title='Genera of integral lattices search error',
             columns=genus_columns,
             shortcuts={'download': Downloader(db.lat_genera),
                        'label': lambda info: genus_by_label_or_name(info.get('label'))},
             postprocess=lattice_search_isometric,
             url_for_label=url_for_label,
             bread=lambda: get_bread("Search results"),
             learnmore=learnmore_list,
             properties=lambda: [])
def genus_search(info, query):
    for field, name in [('rank', 'Rank'), ('det', 'Determinant'), ('level', None),
                        #('minimum', 'Minimal vector length'), ('class_number', None),
                        #('aut', 'Group order')
                        ]:
        parse_ints(info, query, field, name)
    # Check if length of gram is triangular
    gram = info.get('rep')
    #if gram and not (9 + 8*ZZ(gram.count(','))).is_square():
    #    flash_error("%s is not a valid input for Gram matrix.  It must be a list of integer vectors of triangular length, such as [1,2,3].", gram)
    #    raise ValueError
    parse_list(info, query, 'gram', process=vect_to_sym)


@genus_page.route('/<label>')
def render_genus_webpage(**args):
    f = None
    if 'label' in args:
        lab = clean_input(args.get('label'))
        if lab != args.get('label'):
            return redirect(url_for('.render_genus_webpage', label=lab), 301)
        f = db.lat_genera.lucky({'$or': [{'label': lab}]})
    if f is None:
        t = "Integral lattice search error"
        bread = get_bread()
        flash_error("%s is not a valid label or name for an integral lattice in the database.", lab)
        return render_template("lattice-error.html", title=t, properties=[], bread=bread, learnmore=learnmore_list())
    info = {}
    info.update(f)

    info['friends'] = []

    bread = get_bread(f['label'])
    info['rank'] = int(f['rank'])
    info['det'] = int(f['det'])
    info['level'] = int(f['level'])
    info['gram'] = vect_to_matrix(vect_to_sym(f['rep']))

# This part code was for the dynamic knowl with comments, since the test is displayed this is redundant
#    if info['name'] != "" or info['comments'] !="":
#        info['knowl_args']= "name=%s&report=%s" %(info['name'], info['comments'].replace(' ', '-space-'))
    info['properties'] = [
        ('Rank', prop_int_pretty(info['rank'])),
        ('Determinant', prop_int_pretty(info['det'])),
        ('Level', prop_int_pretty(info['level']))]
    downloads = [("Underlying data", url_for(".genus_data", label=lab))]

    t = "Genus of integral lattices "+info['label']
#    friends = [('L-series (not available)', ' ' ),('Half integral weight modular forms (not available)', ' ')]
    return render_template(
        "genus-single.html",
        info=info,
        title=t,
        bread=bread,
        properties=info['properties'],
        downloads=downloads,
        learnmore=learnmore_list(),
        KNOWL_ID="lattice.%s" % info['label'])
# friends=friends


def vect_to_sym(v):
    n = ZZ(round(sqrt(len(v))))
    M = matrix(n)
    k = 0
    for i in range(n):
        for j in range(n):
            M[i, j] = v[k]
            k += 1
    return [[int(M[i, j]) for i in range(n)] for j in range(n)]


@genus_page.route('/data/<label>')
def genus_data(label):
    if not genus_label_regex.fullmatch(label):
        return abort(404, f"Invalid label {label}")
    bread = get_bread([(label, url_for_label(label)), ("Data", " ")])
    title = f"Genus data - {label}"
    return datapage(label, "lat_genera", title=title, bread=bread)

# data quality pages
@genus_page.route("/Source")
def how_computed_page():
    t = 'Source and acknowledgments for integral lattices'
    bread = get_bread("Source")
    return render_template("double.html", kid='rcs.source.lattice', kid2='rcs.ack.lattice',
                           title=t, bread=bread, learnmore=learnmore_list_remove('Source'))


@genus_page.route("/Completeness")
def completeness_page():
    t = 'Completeness of integral lattice data'
    bread = get_bread("Completeness")
    return render_template("single.html", kid='rcs.cande.lattice',
                           title=t, bread=bread, learnmore=learnmore_list_remove('Completeness'))


@genus_page.route("/Reliability")
def reliability_page():
    t = 'Reliability of integral lattice data'
    bread = get_bread("Reliability")
    return render_template("single.html", kid='rcs.rigor.lattice',
                           title=t, bread=bread, learnmore=learnmore_list_remove('Reliability'))


@genus_page.route("/Labels")
def labels_page():
    t = 'Genera of integral lattice labels'
    bread = get_bread("Labels")
    return render_template("single.html", kid='lattice.label',
                           title=t, bread=bread, learnmore=learnmore_list_remove('Labels'))

@genus_page.route("/History")
def history_page():
    t = 'A brief history of lattices'
    bread = get_bread("History")
    return render_template("single.html", kid='lattice.history',
                           title=t, bread=bread, learnmore=learnmore_list_remove('History'))

@genus_page.route('/<label>/download/<lang>/<obj>')
def render_genus_webpage_download(**args):
    if args['obj'] == 'shortest_vectors':
        response = make_response(download_genera_full_lists_v(**args))
        response.headers['Content-type'] = 'text/plain'
        return response
    elif args['obj'] == 'genus_reps':
        response = make_response(download_genera_full_lists_g(**args))
        response.headers['Content-type'] = 'text/plain'
        return response


def download_genera_full_lists_v(**args):
    label = str(args['label'])
    res = db.lat_genera.lookup(label)
    mydate = time.strftime("%d %B %Y")
    if res is None:
        return "No such genus"
    lang = args['lang']
    c = download_comment_prefix[lang]
    outstr += download_assignment_start[lang] + '\\\n'
    outstr += download_assignment_end[lang]
    outstr += '\n'
    return outstr


def download_genera_full_lists_g(**args):
    label = str(args['label'])
    res = db.lat_genera.lookup(label, projection=['genus_reps'])
    mydate = time.strftime("%d %B %Y")
    if res is None:
        return "No such lattice"
    lang = args['lang']
    c = download_comment_prefix[lang]
    mat_start = "Mat(" if lang == 'gp' else "Matrix("
    mat_end = "~)" if lang == 'gp' else ")"

    def entry(r):
        return "".join([mat_start, str(r), mat_end])

    outstr += download_assignment_start[lang] + '[\\\n'
    outstr += ",\\\n".join(entry(r) for r in [res['rep']])
    outstr += ']'
    outstr += download_assignment_end[lang]
    outstr += '\n'
    return outstr


class GenusSearchArray(SearchArray):
    noun = "genus"
    sorts = [("rank", "signature", ['rank', 'signature', 'det', 'level', 'label']),
             ("det", "determinant", ['det', 'rank', 'signature', 'level', 'label']),
             ("level", "level", ['level', 'rank', 'signature', 'det', 'label']),
            ]

    def __init__(self):
        rank = TextBox(
            name="rank",
            label="Rank",
            knowl="lattice.dimension",
            example="3",
            example_span="3 or 2-5")
        signature=TextBox(
            name="signature",
            label="Signature",
            knowl="lattice.signature",
            example="3",
            example_span="3 or 2-5"
            )
        det = TextBox(
            name="det",
            label="Determinant",
            knowl="lattice.determinant",
            example="1",
            example_span="1 or 10-100")
        level = TextBox(
            name="level",
            label="Level",
            knowl="lattice.level",
            example="48",
            example_span="48 or 40-100")
        gram = TextBox(
            name="gram",
            label="Gram matrix",
            knowl="lattice.gram",
            example="[5,1,23]",
            example_span=r"$[5,1,23]$ for the matrix $\begin{pmatrix}5 & 1\\ 1& 23\end{pmatrix}$")
        count = CountBox()

        self.browse_array = [[rank], [signature], [det], [level], [gram], [count]]

        self.refine_array = [[rank, signature, det, level, gram] ]
