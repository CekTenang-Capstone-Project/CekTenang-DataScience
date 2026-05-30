"""
Refine insight text using deterministic template mapping.

Input default:
    data/processed/insights_clean.csv
    data/mapping/insight_text_template_mapping.csv

Output default:
    data/processed/insights_final.csv
    outputs/reports/insight_text_refinement_validation.md
"""

from pathlib import Path
import argparse
import pandas as pd

FORBIDDEN_WORDS = ["lo", "gua", "gue", "elo", "kamu", "anda", "pengguna"]


def validate_no_forbidden_words(series: pd.Series) -> list[str]:
    violations = []
    for value in series.dropna().astype(str).unique():
        lower_value = value.lower()
        for word in FORBIDDEN_WORDS:
            tokens = lower_value.replace(",", " ").replace(".", " ").replace(";", " ").split()
            if word in tokens:
                violations.append(f"{word}: {value}")
    return violations


def refine_insights(input_path: Path, mapping_path: Path, output_path: Path, report_path: Path) -> dict:
    df = pd.read_csv(input_path)
    mapping = pd.read_csv(mapping_path)

    required_input_columns = {"id", "period_type", "insight_text"}
    required_mapping_columns = {"template_code", "original_insight_text", "revised_insight_text"}

    missing_input = required_input_columns - set(df.columns)
    missing_mapping = required_mapping_columns - set(mapping.columns)
    if missing_input:
        raise ValueError(f"Kolom input tidak lengkap: {sorted(missing_input)}")
    if missing_mapping:
        raise ValueError(f"Kolom mapping tidak lengkap: {sorted(missing_mapping)}")

    if mapping["original_insight_text"].duplicated().any():
        duplicated = mapping.loc[mapping["original_insight_text"].duplicated(), "original_insight_text"].tolist()
        raise ValueError(f"original_insight_text duplikat pada mapping: {duplicated[:5]}")

    revised_map = dict(zip(mapping["original_insight_text"], mapping["revised_insight_text"]))
    code_map = dict(zip(mapping["original_insight_text"], mapping["template_code"]))

    unmapped = sorted(set(df["insight_text"].dropna()) - set(revised_map))
    if unmapped:
        raise ValueError(f"Ada insight_text yang belum termapping: {unmapped[:10]}")

    violations = validate_no_forbidden_words(mapping["revised_insight_text"])
    if violations:
        raise ValueError("Template mengandung kata yang dilarang:\n" + "\n".join(violations[:10]))

    final_df = df.copy()
    final_df["insight_text_original"] = final_df["insight_text"]
    final_df["insight_template_code"] = final_df["insight_text"].map(code_map)
    final_df["insight_text"] = final_df["insight_text"].map(revised_map)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)

    checks = {
        "input_rows": len(df),
        "output_rows": len(final_df),
        "unique_original_insight_text": int(df["insight_text"].nunique()),
        "mapping_rows": len(mapping),
        "unique_revised_insight_text": int(mapping["revised_insight_text"].nunique()),
        "missing_revised_text": int(final_df["insight_text"].isna().sum()),
        "unmapped_original_text_count": len(unmapped),
        "duplicate_id_count": int(final_df["id"].duplicated().sum()) if "id" in final_df else None,
        "period_type_distribution": final_df["period_type"].value_counts(dropna=False).to_dict(),
    }

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = [
        "# Insight Text Refinement Validation Report",
        "",
        "## Tujuan",
        "Dokumen ini mencatat validasi hasil refinement teks insight berbasis deterministic template mapping. Proses ini hanya mengubah teks display insight dan tidak mengubah relasi utama dataset.",
        "",
        "## Input dan Output",
        f"- Input: `{input_path}`",
        f"- Mapping: `{mapping_path}`",
        f"- Output: `{output_path}`",
        "- Metode: `deterministic_template_mapping_v1`",
        "",
        "## Ringkasan Validasi",
        "| Validasi | Nilai |",
        "|---|---:|",
        f"| Jumlah baris input | {checks['input_rows']} |",
        f"| Jumlah baris output | {checks['output_rows']} |",
        f"| Jumlah unique original insight_text | {checks['unique_original_insight_text']} |",
        f"| Jumlah baris mapping | {checks['mapping_rows']} |",
        f"| Jumlah unique revised insight_text | {checks['unique_revised_insight_text']} |",
        f"| Missing revised insight_text | {checks['missing_revised_text']} |",
        f"| Original insight_text yang tidak termapping | {checks['unmapped_original_text_count']} |",
        f"| Duplicate id pada output | {checks['duplicate_id_count']} |",
        "",
        "## Distribusi Period Type",
        pd.Series(checks["period_type_distribution"]).to_markdown(),
        "",
        "## Catatan",
        "- Kolom `insight_text` pada output final berisi teks formal hasil mapping.",
        "- Kolom `insight_text_original` tetap disimpan untuk traceability internal.",
        "- Kolom `insight_template_code` disimpan agar pola template dapat diaudit.",
        "- Tidak ada perubahan pada kolom relasi utama dataset.",
        "- Template tidak menggunakan kata subjektif langsung seperti `pengguna`, `kamu`, `Anda`, `lo`, atau `gua`.",
    ]
    report_path.write_text("\n".join(report), encoding="utf-8")
    return checks


def main():
    parser = argparse.ArgumentParser(description="Apply deterministic template mapping to insight text.")
    parser.add_argument("--input", default="data/processed/insights_clean.csv")
    parser.add_argument("--mapping", default="data/mapping/insight_text_template_mapping.csv")
    parser.add_argument("--output", default="data/processed/insights_final.csv")
    parser.add_argument("--report", default="outputs/reports/insight_text_refinement_validation.md")
    args = parser.parse_args()

    checks = refine_insights(
        input_path=Path(args.input),
        mapping_path=Path(args.mapping),
        output_path=Path(args.output),
        report_path=Path(args.report),
    )
    print("Insight text refinement selesai.")
    for key, value in checks.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
