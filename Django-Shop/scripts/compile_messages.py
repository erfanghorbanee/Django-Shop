import os
from pathlib import Path

import polib


def compile_locale_messages(locale_root: Path) -> int:
    count = 0
    for lang_dir in locale_root.iterdir():
        lc_messages = lang_dir / "LC_MESSAGES"
        if not lc_messages.exists() or not lc_messages.is_dir():
            continue
        po_path = lc_messages / "django.po"
        if not po_path.exists():
            continue
        mo_path = lc_messages / "django.mo"
        po = polib.pofile(str(po_path))
        po.save_as_mofile(str(mo_path))
        count += 1
        print(f"Compiled: {po_path} -> {mo_path}")
    return count


if __name__ == "__main__":
    here = Path(__file__).resolve()
    # locale directory is at project root: ../locale
    locale_dir = here.parent.parent / "locale"
    if not locale_dir.exists():
        raise SystemExit(f"Locale directory not found: {locale_dir}")
    compiled = compile_locale_messages(locale_dir)
    print(f"Done. Compiled {compiled} locale(s).")