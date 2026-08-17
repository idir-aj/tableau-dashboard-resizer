"""
Application standalone — Redimensionner les dashboards Tableau
Extrait de DashboardResize.py pour fonctionner de manière autonome.

Lancement :
    streamlit run app_resize.py
"""

import streamlit as st
import streamlit_antd_components as sac
import pandas as pd

from utils import (
    charger_contenu_xml,
    parser_xml,
    remballer_twbx,
)
from outil_resize import (
    recuperer_dashboards_avec_tailles,
    modifier_tableaux_de_bord,
    init_df_resize,
)

# ═══════════════════════════════════════════════════════════════
# TRADUCTIONS
# ═══════════════════════════════════════════════════════════════

TRANSLATIONS = {
    "fr": {
        "title":        "📐 Redimensionner les dashboards Tableau",
        "upload_label": "Uploader le fichier .twb ou .twbx",
        "upload_error": "❌ Impossible de lire le fichier : {}",
        "tds_not_applicable": "Cet outil ne s'applique pas aux fichiers .tds (source de données sans classeur).",
        "description":       "Modifie les dimensions des dashboards d'un classeur Tableau (.twb / .twbx) et recalcule automatiquement les positions de chaque objet.",
        "resize_apply_all_title":   "Appliquer à tous les dashboards cochés",
        "resize_common_width":      "Largeur commune",
        "resize_common_height":     "Hauteur commune",
        "resize_btn_apply_all":     "↓ Appliquer à tous",
        "resize_warn_no_dim":       "Renseigne au moins une dimension commune.",
        "resize_dashboards_title":  "Dashboards",
        "resize_dashboards_caption": "Cochez les dashboards à modifier et renseignez les nouvelles dimensions.",
        "resize_col_check":  "Modifier",
        "resize_col_dash":   "Dashboard",
        "resize_col_cur_w":  "Largeur act.",
        "resize_col_cur_h":  "Hauteur act.",
        "resize_col_new_w":  "Nouvelle largeur",
        "resize_col_new_h":  "Nouvelle hauteur",
        "resize_toggle_right":      "Déplacer vers la droite",
        "resize_toggle_right_desc": "Repositionne les objets lors d'un agrandissement horizontal",
        "resize_toggle_down":       "Déplacer vers le bas",
        "resize_toggle_down_desc":  "Repositionne les objets lors d'un agrandissement vertical",
        "resize_btn":        "Modifier ({n} dashboard{s} sélectionné{s})",
        "resize_error_dims": "Dimensions manquantes pour : **{}**",
        "resize_success":    "✅ {} dashboard(s) modifié(s).",
        "resize_download":   "⬇️ Télécharger le fichier modifié",
        "resize_no_dashboard": "Aucun dashboard trouvé dans ce fichier.",
        "resize_suffix":     "_redimensionné",
        "steps_expander":    "📋 Comment utiliser cet outil",
        "steps_content":     """
**Étape 1 — Charger le classeur**
Uploadez votre fichier **.twb** ou **.twbx** via le bouton ci-dessous.

---

**Étape 2 — Appliquer les mêmes dimensions à tous les dashboards** *(optionnel)*
Saisissez une largeur et/ou une hauteur commune, cochez les dashboards à affecter, puis cliquez sur **↓ Appliquer à tous**.

*— ou —*

**Étape 3 — Modifier chaque dashboard individuellement**
Dans le tableau, cochez les dashboards à redimensionner et renseignez leurs nouvelles dimensions ligne par ligne.

---

**Étape 4 — Lancer la modification**
Cliquez sur le bouton **Modifier** en bas de page.

**Étape 5 — Télécharger le résultat**
Un bouton **Télécharger** apparaît : cliquez dessus pour récupérer le fichier modifié.
""",
    },
    "en": {
        "title":        "📐 Resize Tableau Dashboards",
        "upload_label": "Upload the .twb or .twbx file",
        "upload_error": "❌ Unable to read the file: {}",
        "tds_not_applicable": "This tool does not apply to .tds files (data source without workbook).",
        "description":       "Resize the dashboards of a Tableau workbook (.twb / .twbx) and automatically recalculate the position of every object.",
        "resize_apply_all_title":   "Apply to all checked dashboards",
        "resize_common_width":      "Common width",
        "resize_common_height":     "Common height",
        "resize_btn_apply_all":     "↓ Apply to all",
        "resize_warn_no_dim":       "Enter at least one common dimension.",
        "resize_dashboards_title":  "Dashboards",
        "resize_dashboards_caption": "Check the dashboards to modify and enter the new dimensions.",
        "resize_col_check": "Modify",
        "resize_col_dash":  "Dashboard",
        "resize_col_cur_w": "Current width",
        "resize_col_cur_h": "Current height",
        "resize_col_new_w": "New width",
        "resize_col_new_h": "New height",
        "resize_toggle_right":      "Move to the right",
        "resize_toggle_right_desc": "Repositions objects when expanding horizontally",
        "resize_toggle_down":       "Move downward",
        "resize_toggle_down_desc":  "Repositions objects when expanding vertically",
        "resize_btn":        "Modify ({n} dashboard{s} selected)",
        "resize_error_dims": "Missing dimensions for: **{}**",
        "resize_success":    "✅ {} dashboard(s) modified.",
        "resize_download":   "⬇️ Download modified file",
        "resize_no_dashboard": "No dashboard found in this file.",
        "resize_suffix":     "_resized",
        "steps_expander":    "📋 How to use this tool",
        "steps_content":     """
**Step 1 — Load the workbook**
Upload your **.twb** or **.twbx** file using the button below.

---

**Step 2 — Apply the same dimensions to all dashboards** *(optional)*
Enter a common width and/or height, check the dashboards to affect, then click **↓ Apply to all**.

*— or —*

**Step 3 — Modify each dashboard individually**
In the table, check the dashboards to resize and enter their new dimensions row by row.

---

**Step 4 — Run the modification**
Click the **Modify** button at the bottom of the page.

**Step 5 — Download the result**
A **Download** button will appear: click it to retrieve the modified file.
""",
    },
}


# ═══════════════════════════════════════════════════════════════
# APPLICATION PRINCIPALE
# ═══════════════════════════════════════════════════════════════

def main():
    # ── Sélecteur de langue ────────────────────────────────────────
    _col_title, _col_lang = st.columns([5, 1])
    with _col_lang:
        st.write("")
        _choice = st.radio(
            "",
            options=["🇫🇷 FR", "🇬🇧 EN"],
            horizontal=True,
            key="lang_radio",
            index=1,
            label_visibility="collapsed",
        )
    lang = "en" if "EN" in _choice else "fr"
    T = TRANSLATIONS[lang]

    with _col_title:
        st.title(T["title"])
        st.caption(T["description"])

    # ── Guide d'utilisation ────────────────────────────────────────
    with st.expander(T["steps_expander"]):
        st.markdown(T["steps_content"])

    # ── Upload ─────────────────────────────────────────────────────
    xml_file = st.file_uploader(T["upload_label"], type=["twb", "twbx"])
    st.divider()

    if xml_file is None:
        return

    # ── Chargement et validation du fichier ────────────────────────
    if xml_file.name.endswith(".tds"):
        st.info(T["tds_not_applicable"])
        return

    try:
        xml_content, format_entree, ressources = charger_contenu_xml(xml_file)
        parser_xml(xml_content)  # validation syntaxique
    except ValueError as e:
        st.error(T["upload_error"].format(e))
        return

    # Réinitialiser si le fichier change
    if st.session_state.get("fichier_actuel") != xml_file.name:
        st.session_state.pop("df_resize", None)
        st.session_state["fichier_actuel"] = xml_file.name
        st.session_state["format_entree"] = format_entree
        st.session_state["ressources_twbx"] = ressources

    # ── Outil de redimensionnement ─────────────────────────────────
    dashboards = recuperer_dashboards_avec_tailles(xml_content)
    if not dashboards:
        st.warning(T["resize_no_dashboard"])
        return

    if "df_resize" not in st.session_state:
        st.session_state["df_resize"] = init_df_resize(dashboards)

    # Appliquer à tous
    st.subheader(T["resize_apply_all_title"])
    col_a, col_b, col_c = st.columns([1, 1, 1])
    with col_a:
        largeur_globale = st.number_input(
            T["resize_common_width"], min_value=1, max_value=3000, value=None,
            step=1, placeholder="Ex : 1600", key="resize_global_w"
        )
    with col_b:
        hauteur_globale = st.number_input(
            T["resize_common_height"], min_value=1, max_value=6000, value=None,
            step=1, placeholder="Ex : 1050", key="resize_global_h"
        )
    with col_c:
        st.write("")
        st.write("")
        if st.button(T["resize_btn_apply_all"], use_container_width=True, key="resize_apply_all"):
            if largeur_globale is None and hauteur_globale is None:
                st.warning(T["resize_warn_no_dim"])
            else:
                df = st.session_state["df_resize"].copy()
                mask = df["Modifier"] == True
                if not mask.any():
                    mask = pd.Series([True] * len(df), index=df.index)
                if largeur_globale is not None:
                    df.loc[mask, "Nouvelle largeur"] = float(largeur_globale)
                if hauteur_globale is not None:
                    df.loc[mask, "Nouvelle hauteur"] = float(hauteur_globale)
                st.session_state["df_resize"] = df
                st.rerun()

    # Tableau éditeur
    st.subheader(T["resize_dashboards_title"])
    st.caption(T["resize_dashboards_caption"])
    edited_resize = st.data_editor(
        st.session_state["df_resize"],
        column_config={
            "Modifier":         st.column_config.CheckboxColumn(T["resize_col_check"], width="small"),
            "Dashboard":        st.column_config.TextColumn(T["resize_col_dash"], disabled=True),
            "Largeur actuelle": st.column_config.TextColumn(T["resize_col_cur_w"], disabled=True, width="small"),
            "Hauteur actuelle": st.column_config.TextColumn(T["resize_col_cur_h"], disabled=True, width="small"),
            "Nouvelle largeur": st.column_config.NumberColumn(T["resize_col_new_w"], min_value=1, max_value=3000, step=1),
            "Nouvelle hauteur": st.column_config.NumberColumn(T["resize_col_new_h"], min_value=1, max_value=6000, step=1),
        },
        hide_index=True,
        use_container_width=True,
        key="editor_resize",
    )

    # Toggles de repositionnement
    st.divider()
    col_l, col_r = st.columns(2)
    with col_l:
        deplacer_droite = sac.switch(
            label=T["resize_toggle_right"],
            description=T["resize_toggle_right_desc"],
            value=False, align="start", size="xs", position="left", key="toggle_droite"
        )
    with col_r:
        deplacer_bas = sac.switch(
            label=T["resize_toggle_down"],
            description=T["resize_toggle_down_desc"],
            value=False, align="start", size="xs", position="left", key="toggle_bas"
        )

    # Bouton principal
    nb_coches_resize = int(edited_resize["Modifier"].sum())
    s = "s" if nb_coches_resize > 1 else ""
    st.write("")
    if st.button(
        T["resize_btn"].format(n=nb_coches_resize, s=s),
        type="primary",
        disabled=nb_coches_resize == 0,
        key="btn_resize",
    ):
        selection = edited_resize[edited_resize["Modifier"]]
        lignes_ko = selection[
            selection["Nouvelle largeur"].isna() | selection["Nouvelle hauteur"].isna()
        ]
        if not lignes_ko.empty:
            st.error(T["resize_error_dims"].format(", ".join(lignes_ko["Dashboard"].tolist())))
        else:
            modifications = {
                row["Dashboard"]: (int(row["Nouvelle largeur"]), int(row["Nouvelle hauteur"]))
                for _, row in selection.iterrows()
            }
            try:
                fichier = modifier_tableaux_de_bord(
                    xml_content, modifications, deplacer_droite, deplacer_bas
                )
                st.success(T["resize_success"].format(nb_coches_resize))

                nom_base = xml_file.name.replace(".twbx", "").replace(".twb", "")

                # Format de sortie : .twbx si l'entrée était un .twbx avec ressources
                if (
                    st.session_state.get("format_entree") == "twbx"
                    and st.session_state.get("ressources_twbx")
                ):
                    fichier_telecharge = remballer_twbx(fichier, st.session_state["ressources_twbx"])
                    ext = ".twbx"
                    mime = "application/zip"
                else:
                    fichier_telecharge = fichier
                    ext = ".twb"
                    mime = "application/xml"

                st.download_button(
                    label=T["resize_download"],
                    data=fichier_telecharge,
                    file_name=f"{nom_base}{T['resize_suffix']}{ext}",
                    mime=mime,
                    key="dl_resize",
                )
            except ValueError as e:
                st.error(str(e))


if __name__ == "__main__":
    st.set_page_config(
        page_title="Resize Tableau",
        page_icon="📐",
        layout="wide",
    )
    main()
