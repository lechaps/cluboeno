#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Extraction des contenus marqués par <i class="fa fa-plus-circle"></i> dans des contenus Hugo.

- Parcourt ./content/club/ puis ./content/post/ (dans cet ordre)
- Détecte :
  1) Titres Markdown ##..###### contenant l'icône → capture la section complète
  2) Lignes (listes, paragraphes...) contenant l'icône → crée une mini-section
- Classe les extraits en deux catégories :
  A) DOUBLE PLUS : deux icônes sur la même ligne
  B) PLUS : une seule icône

- Génère un nouvel article Hugo :
  categories = ["Dégustations"]
  date = <ISO UTC actuelle>
  tags = []
  title = "Le classement officiel des vins du Club Oeno : les “PLUS”"
  writer = "Romain"

- Structure du rendu :
  ## La partie DOUBLE PLUS (compteur)
     _Club : X (dernier ajout : …) • Articles : Y (dernier ajout : …)_
     … vins …
  ## La partie PLUS (compteur)
     _Club : X (dernier ajout : …) • Articles : Y (dernier ajout : …)_
     … vins …
"""

import os
import re
from datetime import datetime, timezone

# --------- Réglages ----------
DIRECTORIES = ["./content/club/", "./content/post/"]
OUTPUT_PATH = "./content/post/club-classement.md"
ICON_HTML = '<i class="fa fa-plus-circle"></i>'
# ----------------------------

FRONTMATTER_TOML_RE = re.compile(
    r'^\+\+\+\s*(?P<inner>.*?)^\+\+\+',
    flags=re.DOTALL | re.MULTILINE
)
KV_RE = re.compile(r'^\s*([a-zA-Z0-9_-]+)\s*=\s*(.+?)\s*$', flags=re.MULTILINE)
HEADER_RE = re.compile(r'(?m)^(?P<hashes>#{2,6})\s+(?P<title>.*)$')
ICON_INLINE_RE = re.compile(re.escape(ICON_HTML), flags=re.IGNORECASE)
HR_SPLIT_RE = re.compile(r'(?m)^\s*---\s*$')


def parse_frontmatter_toml(text):
    """Extrait un front matter TOML minimal (+++ ... +++)."""
    m = FRONTMATTER_TOML_RE.search(text)
    if not m:
        return {}, None
    inner = m.group("inner")
    meta = {}
    for km in KV_RE.finditer(inner):
        key, raw_val = km.group(1), km.group(2).strip()
        if raw_val.startswith('[') and raw_val.endswith(']'):
            meta[key] = re.findall(r'"([^"]+)"', raw_val)
        elif raw_val.startswith('"') and raw_val.endswith('"'):
            meta[key] = raw_val.strip('"')
        else:
            meta[key] = raw_val
    return meta, m.group(0)


def path_to_hugo_url(path):
    """Transforme un chemin ./content/... en /club/... ou /post/..."""
    rel = path.replace("\\", "/")
    if rel.startswith("./"):
        rel = rel[2:]
    if rel.startswith("content/"):
        rel = rel[len("content/") :]
    return "/" + rel.replace(".md", "/")


def clean_wine_title(title: str) -> str:
    """Supprime le préfixe 'X -' / 'X –' / 'X —' et normalise le titre."""
    cleaned = re.sub(r'^\s*\d+\s*[–—-]\s*', '', title).strip()
    return cleaned


def parse_source_date(meta_date_str: str, fallback_epoch: float) -> datetime:
    """Parse la date ISO du front matter; repli sur mtime, renvoie UTC-aware."""
    if isinstance(meta_date_str, str) and meta_date_str:
        s = meta_date_str.strip()
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            else:
                dt = dt.astimezone(timezone.utc)
            return dt
        except Exception:
            pass
    return datetime.fromtimestamp(fallback_epoch, tz=timezone.utc)


def format_date_for_display(dt: datetime) -> str:
    """Formate une date UTC en français (ex: 6 novembre 2025)."""
    mois_fr = [
        "janvier", "février", "mars", "avril", "mai", "juin",
        "juillet", "août", "septembre", "octobre", "novembre", "décembre"
    ]
    try:
        return f"{dt.day} {mois_fr[dt.month - 1]} {dt.year}"
    except Exception:
        return dt.strftime("%Y-%m-%d")


def latest_dt_str(seq):
    """Retourne la date la plus récente (formatée) d'une liste [(dt, section_md), ...]."""
    if not seq:
        return "—"
    last_dt = max(dt for dt, _ in seq)
    return format_date_for_display(last_dt)


def _count_icons(s: str) -> int:
    """Compte les occurrences exactes de l'icône dans une ligne."""
    return len(re.findall(re.escape(ICON_HTML), s, flags=re.IGNORECASE))


def extract_sections_with_icon(content, source_url, source_title, src_dt):
    """
    Retourne deux listes :
      sections_single: [markdown_section, ...] pour 1 icône
      sections_double: [markdown_section, ...] pour 2+ icônes
    - Titres transformés en ### et nettoyés de 'X - / X – / X —'
    - Ajoute la ligne '_dégusté le : …_'
    - Lien en bas de bloc vers l'article source (texte = titre Hugo)
    """
    sections_single = []
    sections_double = []

    headers = []
    for m in HEADER_RE.finditer(content):
        start, end = m.start(), m.end()
        level = len(m.group('hashes'))
        title = m.group('title')
        full_line = m.group(0)
        headers.append((start, end, level, title, full_line))

    content_len = len(content)

    # 1) Sections dont le titre contient l'icône
    for i, (start, end, level, title, full_line) in enumerate(headers):
        icon_count = _count_icons(full_line)
        if icon_count == 0:
            continue
        section_end = content_len
        for j in range(i + 1, len(headers)):
            nstart, _, nlevel, _, _ = headers[j]
            if nlevel <= level:
                section_end = nstart
                break
        clean_title = ICON_INLINE_RE.sub("", title).strip()
        clean_title = clean_wine_title(clean_title)
        normalized_header = f"### {clean_title}"
        date_line = f"\n_dégusté le : {format_date_for_display(src_dt)}_"
        body_raw = content[end:section_end]
        m = HR_SPLIT_RE.search(body_raw)
        if m:
            body = body_raw[:m.start()].rstrip()
        else:
            body = body_raw.rstrip()
        link_line = f"\n\n[Lien vers {source_title}]({source_url})"
        section_md = normalized_header + date_line + ("\n\n" + body if body else "") + link_line
        (sections_double if icon_count >= 2 else sections_single).append(section_md.strip())

    # 2) Lignes non-titres avec l'icône (mini-sections)
    seen = set()
    for raw_line in content.splitlines():
        icon_count = _count_icons(raw_line)
        if icon_count == 0:
            continue
        if HEADER_RE.match(raw_line):
            continue  # déjà pris en compte
        line = ICON_INLINE_RE.sub("", raw_line).strip()
        # retire puce/numéro et préfixe numérique
        line = re.sub(r'^\s*([-*+]|\d+\.)\s*', '', line).strip()
        line = clean_wine_title(line)
        if not line:
            continue
        key = (icon_count, line.lower())
        if key in seen:
            continue
        seen.add(key)
        date_line = f"\n_dégusté le : {format_date_for_display(src_dt)}_"
        section = (
            f"### {line}{date_line}\n\n"
            "_Extrait d'une liste — pas de notes détaillées._\n\n"
            f"[Lien vers {source_title}]({source_url})"
        )
        (sections_double if icon_count >= 2 else sections_single).append(section.strip())

    return sections_single, sections_double


def build_frontmatter_toml(date_iso):
    """Front matter fixe pour l'article généré."""
    return (
        "+++\n"
        'categories = ["Dégustations"]\n'
        f'date = "{date_iso}"\n'
        "tags = []\n"
        'title = "Le classement officiel des vins du Club Oeno : les “PLUS”"\n'
        'writer = "Romain"\n'
        "+++\n"
    )


def main():
    # On collecte des tuples: (date_dt, section_md)
    club_single, club_double = [], []
    post_single, post_double = [], []

    for directory in DIRECTORIES:
        for root, _, files in os.walk(directory):
            for fn in files:
                if not fn.endswith(".md"):
                    continue
                if fn == os.path.basename(OUTPUT_PATH):
                    continue  # Ignore le fichier généré
                
                path = os.path.join(root, fn)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        raw = f.read()
                except Exception as e:
                    print(f"[WARN] Lecture échouée pour {path}: {e}")
                    continue

                # Métadonnées + date source
                meta, _ = parse_frontmatter_toml(raw)
                try:
                    mtime = os.path.getmtime(path)
                except Exception:
                    mtime = datetime.now().timestamp()
                src_dt = parse_source_date(meta.get("date", ""), mtime)

                content_wo_fm = FRONTMATTER_TOML_RE.sub("", raw, count=1)
                source_url = path_to_hugo_url(path)
                source_title = meta.get("title", "Article d'origine")

                sections_single, sections_double = extract_sections_with_icon(
                    content_wo_fm, source_url, source_title, src_dt
                )
                if not sections_single and not sections_double:
                    continue

                norm = path.replace("\\", "/")
                is_club = ("/content/club/" in norm or
                           norm.startswith("./content/club/") or
                           norm.startswith("content/club/"))
                if is_club:
                    club_single.extend((src_dt, s) for s in sections_single)
                    club_double.extend((src_dt, s) for s in sections_double)
                else:
                    post_single.extend((src_dt, s) for s in sections_single)
                    post_double.extend((src_dt, s) for s in sections_double)

    if not any([club_single, club_double, post_single, post_double]):
        print(f"[WARN] Aucun contenu trouvé contenant {ICON_HTML}.")
        return

    # Tri décroissant par date
    for seq in (club_single, club_double, post_single, post_double):
        seq.sort(key=lambda t: t[0], reverse=True)

    # ==== Compteurs ====
    count_double_total = len(club_double) + len(post_double)
    count_single_total = len(club_single) + len(post_single)
    count_all = count_double_total + count_single_total

    count_double_club = len(club_double)
    count_double_post = len(post_double)
    count_single_club = len(club_single)
    count_single_post = len(post_single)

    now_iso = datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    parts = [build_frontmatter_toml(now_iso)]

    # ===== TITRE + INTRODUCTION =====
    parts += [
        f"Au fil des dégustations du club et des articles publiés sur le site, certains vins nous ont particulièrement marqué par le **plaisir qu'ils procurent** en regard de leur **prix**. Ils sont indiqué par cet icone rapidement identiable : {ICON_HTML}, les fameux “PLUS”",
        "  ",
        "Cette article rassemble ces coups de cœur sous deux niveaux de notation :",
        "  ",
        f" - **DOUBLE PLUS ({ICON_HTML}{ICON_HTML})** — vins au **rapport prix/plaisir exceptionnel** : de véritables pépites, souvent bluffantes compte tenu de leur tarif.",
        f" - **PLUS ({ICON_HTML})** — vins offrant un **excellent équilibre entre qualité et prix**, que nous recommandons sans hésiter.",
        "  ",
        "> La sélection est classée par ordre chronologique inversé (les plus récentes dégustations en premier) et distinguée selon leur origine :",
        "> **les dégustations du club** d'un côté, et **les articles publiés** de l'autre.",
        "> ",
        "> Chaque vin est présenté avec un lien vers sa fiche ou son article d'origine, afin de retrouver le contexte complet de la dégustation.",
        "",
        f"**Récapitulatif :** {count_all} vins “plussés” — "
        f"{count_double_total} {ICON_HTML}{ICON_HTML}, {count_single_total} {ICON_HTML}.",
        ""
    ]

    # ===== DOUBLE PLUS =====
    if count_double_total > 0:
        parts.append(f"## Les {ICON_HTML}{ICON_HTML} : vins au rapport prix/plaisir exceptionnel")
        parts.append("")

        if club_double:
            parts.append(f"**{count_double_club} vins répertoriés dans des dégustations du club** (dernier ajout : {latest_dt_str(club_double)})")
            parts.append("")
            parts.append(("\n\n---\n\n").join(s for _, s in club_double).rstrip())
            parts.append("")

        if post_double:
            parts.append(f"**{count_double_post} vins répertoriés dans les articles** (dernier ajout : {latest_dt_str(post_double)})")
            parts.append("")
            parts.append(("\n\n---\n\n").join(s for _, s in post_double).rstrip())
            parts.append("")

    # ===== SINGLE PLUS =====
    if count_single_total > 0:
        parts.append(f"## Les {ICON_HTML} : vins avec un excellent équilibre entre qualité et prix")
        parts.append("")

        if club_single:
            parts.append(f"**{count_single_club} vins répertoriés dans des dégustations du club** (dernier ajout : {latest_dt_str(club_single)})")
            parts.append("")
            parts.append(("\n\n---\n\n").join(s for _, s in club_single).rstrip())
            parts.append("")

        if post_single:
            parts.append(f"**{count_single_post} vins répertoriés dans des dégustations du club** (dernier ajout : {latest_dt_str(post_single)})")
            parts.append("")
            parts.append(("\n\n---\n\n").join(s for _, s in post_single).rstrip())
            parts.append("")

    new_article = "\n".join(parts).rstrip() + "\n"

    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(new_article)

    print(f"[OK] Fichier généré : {OUTPUT_PATH}")
    print(f"[INFO] Compteurs → DOUBLE PLUS: total={count_double_total} (club={count_double_club}, articles={count_double_post}); "
          f"PLUS: total={count_single_total} (club={count_single_club}, articles={count_single_post}); "
          f"TOUS: {count_all}")


if __name__ == "__main__":
    main()
