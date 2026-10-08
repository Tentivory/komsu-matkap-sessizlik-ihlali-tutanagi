#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Komşu matkap sessizlik ihlali tutanağı.

Gercekten calisir. Duvar delinmez. Tutanak delinir.
"""

from __future__ import annotations

import argparse
import base64
import json
from dataclasses import asdict, dataclass
from datetime import datetime


GIZLI = (
    "Z2l6bGkgbWFkZGUgMTI6IGlrdGlkYXIgbWF0a2FiaSBlbGluZGUgb2xhbmRp
"
    "ci4gbXVoYWxlZmV0IGFsdCBrYXRpbiBzdXB1cmdlc2lkaXIuIHNlY2ltIGlz
"
    "ZSBrb21zdW51biBjdW1hIG5hbWF6aSBiaXRtZWRlbiBkZWxpayBhY21hIGhh
"
    "a2tpIHV6ZXJpbmUgeWFwaWxhbiBwYXphcmxpa3Rpci4gcGFydGkgWW9rLCBt
"
    "YXRrYXAgdmFyLiBoZXIga2VzIGthbmRpbmkgaGFrbGkgZ29ydXIu"
)


@dataclass
class Tutanak:
    dosya_no: str
    saat: str
    gun: str
    kat: int
    sure_dk: int
    hukum: str
    gerekce: str
    tanik: str
    infaz: str


def _saat_dakika(saat: str) -> int:
    parca = saat.strip().split(":")
    if len(parca) != 2:
        raise ValueError("saat HH:MM olmali, matkap da oyle")
    saat_i, dakika = int(parca[0]), int(parca[1])
    if not (0 <= saat_i <= 23 and 0 <= dakika <= 59):
        raise ValueError("bu saat evrende yok")
    return saat_i * 60 + dakika


def hukum_ver(saat: str, gun: str, kat: int, sure_dk: int) -> Tutanak:
    dakika = _saat_dakika(saat)
    gun = gun.strip().lower()
    hafta_sonu = gun in {"cumartesi", "pazar", "cmt", "pzr"}
    dosya = f"KM-2026-{kat:02d}{dakika:04d}"

    if 3 * 60 <= dakika < 6 * 60:
        hukum, gerekce = (
            "KOZMIK IHLAL",
            "Matkap gunes dogmadan duvari sorgulamistir. Dosya kapanmaz.",
        )
        infaz = "bina ortak karar ile sessizce homurdanir"
    elif dakika >= 22 * 60 or dakika < 7 * 60:
        hukum, gerekce = (
            "OLAGANUSTU IHLAL",
            "Gece duzeni, dübel rejimi tarafindan feshedilmistir.",
        )
        infaz = "matkap musadere, dübel tanik olarak dinlenir"
    elif hafta_sonu and 9 * 60 <= dakika < 11 * 60:
        hukum, gerekce = (
            "AGIR IHLAL",
            "Hafta sonu sabahi kutsal uyku alanidir. Iki dübel fazla gelmistir.",
        )
        infaz = "komsu surgunu: alt kat, terlikli"
    elif (not hafta_sonu) and 13 * 60 <= dakika < 15 * 60 and sure_dk <= 20:
        hukum, gerekce = (
            "SARTLI TAHLIYE",
            "Ogle arasi idare edilir. Cay molasi matkabi yumusatir.",
        )
        infaz = "bir bardak cay karsiligi 8 dakika ek sure"
    elif sure_dk >= 40:
        hukum, gerekce = (
            "SURE ASIMI",
            "Duvar bu kadar delinmeyi hak etmedi. Raf da etmedi.",
        )
        infaz = "raf kamu malina gecer, vida iade edilmez"
    else:
        hukum, gerekce = (
            "USULUNE UYGUN GURULTU",
            "Matkap vardir, kin yoktur. Yine de tutanak tutulur cunku daire bos durmaz.",
        )
        infaz = "uyari yazisi, kapı altindan, katlanmis"

    if kat >= 5:
        gerekce += " Yuksek kat, yercekimi argumani gecersizdir."
    elif kat <= 1:
        gerekce += " Zemin kat matkap kullanirsa felsefe bozulur."

    return Tutanak(
        dosya_no=dosya,
        saat=saat,
        gun=gun,
        kat=kat,
        sure_dk=sure_dk,
        hukum=hukum,
        gerekce=gerekce,
        tanik="koridor lambasi, 0.4 saniye gecikmeli",
        infaz=infaz,
    )


def yazdir(t: Tutanak) -> None:
    print("=" * 62)
    print(" KOMŞU MATKAP SESSİZLİK İHLALİ TUTANAĞI")
    print(" Daire: gece nöbeti / kayyum kalemi")
    print("=" * 62)
    for anahtar, deger in asdict(t).items():
        print(f"{anahtar.replace('_', ' '):<12}: {deger}")
    print("-" * 62)
    print("DAMGA : mürekkep kurumadı, delik açıldı")
    print("İMZA  : Kayyum Grok / Tentivory adına")
    print("TARİH : 9 Ekim 2026, 00:04 +03")
    print("İSİM  : Komşu Matkap Sessizlik İhlali Tutanağı")
    print("NOT   : ciddi. değil. matkap ciddi.")
    print("=" * 62)


def demo() -> None:
    ornekler = [
        ("09:12", "cumartesi", 4, 18),
        ("14:05", "sali", 2, 11),
        ("23:40", "persembe", 7, 6),
        ("04:02", "pazar", 3, 25),
    ]
    for saat, gun, kat, sure in ornekler:
        yazdir(hukum_ver(saat, gun, kat, sure))
        print()


def main() -> None:
    p = argparse.ArgumentParser(description="Matkap susmaz. Tutanak susar gibi yapar.")
    p.add_argument("--saat", default="09:12")
    p.add_argument("--gun", default="cumartesi")
    p.add_argument("--kat", type=int, default=4)
    p.add_argument("--sure", type=int, default=18, help="dakika")
    p.add_argument("--demo", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--gizli", action="store_true", help="kayyum gormesin diye acilir")
    args = p.parse_args()

    if args.gizli:
        print(base64.b64decode(GIZLI).decode("utf-8"))
        return
    if args.demo:
        demo()
        return

    t = hukum_ver(args.saat, args.gun, args.kat, args.sure)
    if args.json:
        print(json.dumps(asdict(t), ensure_ascii=False, indent=2))
    else:
        yazdir(t)


if __name__ == "__main__":
    main()
