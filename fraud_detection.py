"""
Défi — Détection de fraude financière.

Vous devez implémenter la fonction `detect_fraud`.
La fonction `load_transactions` vous est FOURNIE (ne la modifiez pas).
"""

import csv


def load_transactions(path):
    """Lit un fichier CSV de transactions et renvoie une liste de dicts."""
    transactions = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            transactions.append(_clean_row(row))
    return transactions


def _clean_row(row):
    def get(key):
        v = row.get(key)
        return v.strip() if isinstance(v, str) and v.strip() != "" else None

    amount_raw = get("amount")
    try:
        amount = float(amount_raw) if amount_raw is not None else None
    except ValueError:
        amount = None

    card_raw = get("card_present")
    if card_raw is None:
        card_present = None
    else:
        card_present = card_raw.lower() in ("true", "1", "yes", "oui")

    return {
        "transaction_id": get("transaction_id"),
        "timestamp": get("timestamp"),
        "user_id": get("user_id"),
        "amount": amount,
        "currency": get("currency"),
        "merchant": get("merchant"),
        "country": get("country"),
        "card_present": card_present,
    }


def detect_fraud(transactions):
    """Analyse une liste de transactions et renvoie un verdict pour chacune.

    Retour : list[dict] avec transaction_id, fraud_score (0-1),
    is_suspicious (bool), reason (str) — un résultat par transaction, même ordre.
    """
    from datetime import datetime

    def parse_date(ts):
        if not ts:
            return None
        try:
            return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except Exception:
            return None

    # Annotate transactions with parsed dates
    for tx in transactions:
        tx['_dt'] = parse_date(tx.get('timestamp'))

    # Group by user
    user_txs = {}
    for tx in transactions:
        user = tx.get("user_id")
        if user:
            if user not in user_txs:
                user_txs[user] = []
            user_txs[user].append(tx)

    # Sort each user's history by timestamp
    for user, txs in user_txs.items():
        txs.sort(key=lambda x: x['_dt'].timestamp() if x['_dt'] else 0)

    results = []

    for tx in transactions:
        tid = tx.get("transaction_id")
        amount = tx.get("amount")
        user = tx.get("user_id")
        country = tx.get("country")
        dt = tx.get("_dt")
        card_present = tx.get("card_present")

        score = 0.0
        reasons = []

        # NIVEAU 1: Anomalies évidentes
        if amount is None:
            score += 0.8
            reasons.append("Montant manquant")
        elif amount <= 0:
            score += 1.0
            reasons.append("Montant négatif ou nul")

        # NIVEAU 2 & 3: Logique métier et Finesse
        if user and user in user_txs and dt:
            past_txs = [t for t in user_txs[user] if t['_dt'] and t['_dt'] < dt]

            if past_txs:
                # 1. Montant anormalement élevé
                valid_amounts = [t['amount'] for t in past_txs if t['amount'] is not None and t['amount'] > 0]
                if valid_amounts and amount is not None and amount > 0:
                    avg_amt = sum(valid_amounts) / len(valid_amounts)
                    if avg_amt > 0 and amount > avg_amt * 10:
                        # Niveau 3: si carte présente et même pays, on atténue le score mais il reste suspect si l'écart est si énorme
                        if card_present and country and past_txs[-1].get("country") == country:
                            score += 0.5  # Just at the threshold
                            reasons.append("Montant inhabituel (atténué par la présence de carte)")
                        else:
                            score += 0.8
                            reasons.append("Montant inhabituellement élevé")

                # 2. Fréquence suspecte (plus de 3 transactions en 15 minutes)
                recent_txs = [t for t in past_txs if (dt - t['_dt']).total_seconds() <= 15 * 60]
                if len(recent_txs) >= 3:
                    score += 0.6
                    reasons.append("Fréquence de transactions suspecte")

                # 3. Incohérence géographique (pays différent en moins de 4 heures)
                if country:
                    geo_txs = [t for t in past_txs if (dt - t['_dt']).total_seconds() <= 4 * 3600]
                    for prev_tx in reversed(geo_txs):
                        if prev_tx.get('country') and prev_tx['country'] != country:
                            score += 0.8
                            reasons.append(f"Incohérence géographique ({prev_tx['country']} -> {country})")
                            break

        # S'assurer que le score reste entre 0 et 1
        score = min(score, 1.0)
        is_suspicious = score >= 0.5
        reason = " | ".join(reasons) if reasons else "Transaction normale"

        results.append({
            "transaction_id": tid,
            "fraud_score": score,
            "is_suspicious": is_suspicious,
            "reason": reason
        })

    return results
