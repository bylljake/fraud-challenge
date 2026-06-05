"""
Interface Streamlit — À CRÉER PAR VOUS pour le jury.

Le jury lancera :  streamlit run app.py

Règles :
  - Ne modifiez pas l'appel à detect_fraud / load_transactions (contrat technique).
  - Personnalisez render_interface() : clarté, intuitivité, compréhension pour un public non technique.
  - L'interface n'est PAS notée par la CI ; elle sert au jury pour repêcher et comparer les candidats.
"""

from pathlib import Path

import streamlit as st

from fraud_detection import detect_fraud, load_transactions

SAMPLE_CSV = Path(__file__).parent / "data" / "sample_transactions.csv"


def render_interface(transactions: list[dict], results: list[dict]) -> None:
    """
    ══════════════════════════════════════════════════════════════════
    À COMPLÉTER — votre interface intuitive pour le jury / le public.
    ══════════════════════════════════════════════════════════════════

    Idées (libres) :
      - titres et textes en langage simple (« transaction suspecte », « client à risque ») ;
      - cartes / indicateurs visuels (nombre d'alertes, niveau de risque) ;
      - tableau ou liste filtrable (uniquement les suspectes, par client, par pays…) ;
      - codes couleur, icônes, graphiques ;
      - zone « comment l'IA / vos règles décident » pour expliquer une alerte.

    Le jury évalue : clarté, utilité, intuitivité — pas le code en lui-même.
    """
    import pandas as pd
    import altair as alt

    st.subheader("📊 Tableau de Bord : Analyse des Fraudes")
    
    df_tx = pd.DataFrame(transactions)
    df_res = pd.DataFrame(results)
    
    # Merge both for easy display
    df = pd.merge(df_tx, df_res, on="transaction_id")
    
    total_tx = len(df)
    suspicious_count = df["is_suspicious"].sum()
    legit_count = total_tx - suspicious_count
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("Transactions Analysées", total_tx)
    col2.metric("Transactions Suspectes", suspicious_count, delta_color="inverse", delta=f"{suspicious_count}")
    col3.metric("Taux de Fraude", f"{(suspicious_count/total_tx)*100:.1f}%" if total_tx else "0%")
    
    st.divider()
    
    if suspicious_count > 0:
        st.warning(f"⚠️ {suspicious_count} transaction(s) nécessitent votre attention immédiate.")
    else:
        st.success("✅ Aucune fraude détectée sur cet échantillon.")
        
    col_chart1, col_chart2 = st.columns([2, 1])
    
    with col_chart1:
        st.markdown("### 📈 Répartition des Scores de Fraude")
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("fraud_score:Q", bin=alt.Bin(maxbins=20), title="Score de Fraude"),
            y=alt.Y("count()", title="Nombre de transactions"),
            color=alt.condition(
                alt.datum.fraud_score >= 0.5,
                alt.value("red"),
                alt.value("green")
            ),
            tooltip=["count()", "fraud_score"]
        ).properties(height=300)
        st.altair_chart(chart, use_container_width=True)
        
    with col_chart2:
        st.markdown("### 🔍 Détails par Verdict")
        pie = alt.Chart(df).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="is_suspicious", type="nominal", aggregate="count"),
            color=alt.Color("is_suspicious:N", scale=alt.Scale(domain=[False, True], range=['#28a745', '#dc3545']), legend=alt.Legend(title="Est suspecte")),
            tooltip=["is_suspicious", "count()"]
        ).properties(height=300)
        st.altair_chart(pie, use_container_width=True)

    st.markdown("### 📋 Historique des Transactions")
    
    filter_suspicious = st.checkbox("Afficher uniquement les transactions suspectes", value=True)
    
    df_display = df.copy()
    if filter_suspicious:
        df_display = df_display[df_display["is_suspicious"] == True]
        
    st.dataframe(
        df_display[["transaction_id", "user_id", "amount", "country", "fraud_score", "reason", "is_suspicious"]],
        use_container_width=True,
        column_config={
            "transaction_id": "ID",
            "user_id": "Client",
            "amount": st.column_config.NumberColumn("Montant", format="$ %.2f"),
            "country": "Pays",
            "fraud_score": st.column_config.ProgressColumn(
                "Score de risque",
                format="%.2f",
                min_value=0,
                max_value=1,
            ),
            "reason": "Explication",
            "is_suspicious": "Suspect"
        }
    )


def main() -> None:
    st.set_page_config(
        page_title="Détection de fraude — Hackathon INTELO2026",
        page_icon="🛡️",
        layout="wide",
    )

    st.title("Détection de fraude financière")
    st.caption("Hackathon INTELO2026 — interface participant · évaluée par le jury")

    with st.sidebar:
        st.header("Charger des données")
        use_sample = st.toggle("Utiliser le fichier d'exemple", value=True)
        transactions: list[dict] = []

        if use_sample:
            transactions = load_transactions(str(SAMPLE_CSV))
            st.success(f"{len(transactions)} transactions (exemple)")
        else:
            uploaded = st.file_uploader("Importer un CSV", type=["csv"])
            if uploaded:
                tmp = Path(".streamlit_upload.csv")
                tmp.write_bytes(uploaded.getvalue())
                transactions = load_transactions(str(tmp))
                tmp.unlink(missing_ok=True)
                st.success(f"{len(transactions)} transactions importées")

        st.divider()
        st.markdown(
            "**Jury :** évaluez l'ergonomie et la clarté de l'écran principal, "
            "pas seulement le score des tests."
        )

    if not transactions:
        st.info("Chargez des transactions (barre latérale) puis lancez l'analyse.")
        return

    if st.button("Analyser", type="primary"):
        try:
            results = detect_fraud(transactions)
        except NotImplementedError:
            st.error("Implémentez d'abord `detect_fraud` dans `fraud_detection.py`.")
            return
        except Exception as exc:
            st.error(f"Erreur : {exc}")
            return

        render_interface(transactions, results)


if __name__ == "__main__":
    main()
