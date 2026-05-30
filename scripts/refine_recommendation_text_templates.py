"""
Refine recommendation text using deterministic template mapping.

Default input:
    data/processed/recommendations_clean.csv
    data/mapping/recommendation_text_template_mapping.csv

Default output:
    data/processed/recommendations_final.csv
    outputs/reports/recommendation_text_refinement_validation.md

Scope:
    - Only recommendation_text is refined.
    - title, category, priority_level, period_type, IDs, and relationship columns are preserved.
"""

from pathlib import Path
import argparse
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_WORDS = ["lo", "gua", "gue", "elo", "kamu", "anda", "pengguna"]

KEY_COLUMNS = [
    "title",
    "category",
    "priority_level",
    "period_type",
    "recommendation_text",
]

MAPPING_KEY_COLUMNS = [
    "title",
    "category",
    "priority_level",
    "period_type",
    "original_recommendation_text",
]


def resolve_project_path(path_value: str) -> Path:
    """Resolve relative path from project root, not from current terminal directory."""
    path = Path(path_value)
    if path.is_absolute():
        return path
    return PROJECT_ROOT / path


def find_input_file(input_path: Path) -> Path:
    """
    Fallback input finder.

    Priority:
    1. Provided input path
    2. data/processed/recommendations_clean.csv
    3. data/processed/recommendations.csv
    4. data/raw/recommendations.csv
    """
    candidates = [
        input_path,
        PROJECT_ROOT / "data" / "processed" / "recommendations_clean.csv",
        PROJECT_ROOT / "data" / "processed" / "recommendations.csv",
        PROJECT_ROOT / "data" / "raw" / "recommendations.csv",
    ]

    for candidate in candidates:
        if candidate.exists():
            return candidate

    raise FileNotFoundError(
        "File input recommendation tidak ditemukan. Cek salah satu path berikut:\n"
        + "\n".join(str(candidate) for candidate in candidates)
    )


def validate_no_forbidden_words(series: pd.Series) -> list[str]:
    """Return forbidden-word violations using token-based matching."""
    violations = []
    separators = [",", ".", ";", ":", "!", "?", "(", ")", "[", "]", "{", "}", "/", "\\", "\n", "\t"]

    for value in series.dropna().astype(str).unique():
        lower_value = value.lower()
        for separator in separators:
            lower_value = lower_value.replace(separator, " ")
        tokens = lower_value.split()

        for word in FORBIDDEN_WORDS:
            if word in tokens:
                violations.append(f"{word}: {value}")

    return violations


def refine_recommendations(
    input_path: Path,
    mapping_path: Path,
    output_path: Path,
    report_path: Path,
) -> dict:
    df = pd.read_csv(input_path)
    mapping = pd.read_csv(mapping_path)

    required_input_columns = {
        "id",
        "period_type",
        "category",
        "title",
        "recommendation_text",
        "priority_level",
    }

    required_mapping_columns = {
        "template_code",
        "title",
        "category",
        "priority_level",
        "period_type",
        "original_recommendation_text",
        "revised_recommendation_text",
    }

    missing_input = required_input_columns - set(df.columns)
    missing_mapping = required_mapping_columns - set(mapping.columns)

    if missing_input:
        raise ValueError(f"Kolom input tidak lengkap: {sorted(missing_input)}")
    if missing_mapping:
        raise ValueError(f"Kolom mapping tidak lengkap: {sorted(missing_mapping)}")

    if mapping[MAPPING_KEY_COLUMNS].duplicated().any():
        duplicated = mapping.loc[mapping[MAPPING_KEY_COLUMNS].duplicated(), MAPPING_KEY_COLUMNS]
        raise ValueError(
            "Mapping memiliki key duplikat. Contoh duplikasi:\n"
            + duplicated.head(10).to_string(index=False)
        )

    violations = validate_no_forbidden_words(mapping["revised_recommendation_text"])
    if violations:
        raise ValueError(
            "Template rekomendasi mengandung kata yang dilarang:\n"
            + "\n".join(violations[:20])
        )

    mapping_for_merge = mapping.rename(
        columns={"original_recommendation_text": "recommendation_text"}
    )

    original_columns = df.columns.tolist()
    locked_columns = [
        col
        for col in [
            "id",
            "user_id",
            "stress_prediction_id",
            "weekly_summary_id",
            "period_type",
            "category",
            "title",
            "priority_level",
            "created_at",
        ]
        if col in df.columns
    ]

    final_df = df.merge(
        mapping_for_merge[
            [
                "title",
                "category",
                "priority_level",
                "period_type",
                "recommendation_text",
                "template_code",
                "revised_recommendation_text",
            ]
        ],
        on=["title", "category", "priority_level", "period_type", "recommendation_text"],
        how="left",
        validate="many_to_one",
    )

    unmapped_df = final_df[final_df["revised_recommendation_text"].isna()]
    if not unmapped_df.empty:
        examples = (
            unmapped_df[
                ["title", "category", "priority_level", "period_type", "recommendation_text"]
            ]
            .drop_duplicates()
            .head(20)
            .to_string(index=False)
        )
        raise ValueError(
            f"Ada recommendation_text yang belum termapping: {len(unmapped_df)} baris.\n"
            f"Contoh:\n{examples}"
        )

    # Preserve original text for internal traceability.
    final_df["recommendation_text_original"] = final_df["recommendation_text"]
    final_df["recommendation_template_code"] = final_df["template_code"]
    final_df["recommendation_text"] = final_df["revised_recommendation_text"]

    final_df = final_df.drop(columns=["template_code", "revised_recommendation_text"])

    # Keep original columns first, then audit columns.
    audit_columns = ["recommendation_text_original", "recommendation_template_code"]
    final_df = final_df[original_columns + audit_columns]

    # Validate locked columns unchanged.
    locked_changed = {}
    for col in locked_columns:
        if not df[col].equals(final_df[col]):
            locked_changed[col] = int((df[col] != final_df[col]).sum())

    if locked_changed:
        raise ValueError(f"Kolom yang seharusnya tidak berubah ternyata berubah: {locked_changed}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_df.to_csv(output_path, index=False)

    checks = {
        "input_rows": len(df),
        "output_rows": len(final_df),
        "unique_original_recommendation_text": int(df["recommendation_text"].nunique()),
        "mapping_rows": len(mapping),
        "unique_revised_recommendation_text": int(mapping["revised_recommendation_text"].nunique()),
        "missing_revised_text": int(final_df["recommendation_text"].isna().sum()),
        "unmapped_original_text_count": int(unmapped_df.shape[0]),
        "duplicate_id_count": int(final_df["id"].duplicated().sum()) if "id" in final_df else None,
        "title_changed_count": 0,
        "category_changed_count": 0,
        "priority_level_changed_count": 0,
        "period_type_changed_count": 0,
        "period_type_distribution": final_df["period_type"].value_counts(dropna=False).to_dict(),
        "category_distribution": final_df["category"].value_counts(dropna=False).to_dict(),
        "priority_level_distribution": final_df["priority_level"].value_counts(dropna=False).to_dict(),
    }

    # Additional forbidden word scan on final output.
    final_violations = validate_no_forbidden_words(final_df["recommendation_text"])
    checks["forbidden_word_violation_count"] = len(final_violations)

    if final_violations:
        raise ValueError(
            "Output final masih mengandung kata yang dilarang:\n"
            + "\n".join(final_violations[:20])
        )

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report = [
        "# Recommendation Text Refinement Validation Report",
        "",
        "## Tujuan",
        "Dokumen ini mencatat validasi hasil refinement teks rekomendasi berbasis deterministic template mapping. Proses ini hanya mengubah teks display rekomendasi dan tidak mengubah label analitik maupun relasi utama dataset.",
        "",
        "## Input dan Output",
        f"- Input: `{input_path}`",
        f"- Mapping: `{mapping_path}`",
        f"- Output: `{output_path}`",
        "- Metode: `deterministic_template_mapping_v1`",
        "",
        "## Scope Perubahan",
        "- Kolom `recommendation_text` pada output final berisi teks formal hasil mapping.",
        "- Kolom `title`, `category`, `priority_level`, dan `period_type` tidak diubah agar hasil EDA tetap konsisten.",
        "- Kolom `recommendation_text_original` disimpan untuk traceability internal.",
        "- Kolom `recommendation_template_code` disimpan agar pola template dapat diaudit.",
        "",
        "## Ringkasan Validasi",
        "| Validasi | Nilai |",
        "|---|---:|",
        f"| Jumlah baris input | {checks['input_rows']} |",
        f"| Jumlah baris output | {checks['output_rows']} |",
        f"| Jumlah unique original recommendation_text | {checks['unique_original_recommendation_text']} |",
        f"| Jumlah baris mapping | {checks['mapping_rows']} |",
        f"| Jumlah unique revised recommendation_text | {checks['unique_revised_recommendation_text']} |",
        f"| Missing revised recommendation_text | {checks['missing_revised_text']} |",
        f"| Original recommendation_text yang tidak termapping | {checks['unmapped_original_text_count']} |",
        f"| Duplicate id pada output | {checks['duplicate_id_count']} |",
        f"| Perubahan title | {checks['title_changed_count']} |",
        f"| Perubahan category | {checks['category_changed_count']} |",
        f"| Perubahan priority_level | {checks['priority_level_changed_count']} |",
        f"| Perubahan period_type | {checks['period_type_changed_count']} |",
        f"| Pelanggaran kata terlarang | {checks['forbidden_word_violation_count']} |",
        "",
        "## Distribusi Period Type",
        pd.Series(checks["period_type_distribution"]).to_markdown(),
        "",
        "## Distribusi Category",
        pd.Series(checks["category_distribution"]).to_markdown(),
        "",
        "## Distribusi Priority Level",
        pd.Series(checks["priority_level_distribution"]).to_markdown(),
        "",
        "## Catatan",
        "- Template tidak menggunakan kata subjektif langsung seperti `pengguna`, `kamu`, `Anda`, `lo`, atau `gua`.",
        "- Perubahan ini tidak mengubah struktur rekomendasi, label EDA, maupun relasi ke tabel lain.",
    ]

    report_path.write_text("\n".join(report), encoding="utf-8")
    return checks


def main():
    parser = argparse.ArgumentParser(description="Apply deterministic template mapping to recommendation text.")
    parser.add_argument("--input", default="data/processed/recommendations_clean.csv")
    parser.add_argument("--mapping", default="data/mapping/recommendation_text_template_mapping.csv")
    parser.add_argument("--output", default="data/processed/recommendations_final.csv")
    parser.add_argument("--report", default="outputs/reports/recommendation_text_refinement_validation.md")
    args = parser.parse_args()

    input_path = find_input_file(resolve_project_path(args.input))
    mapping_path = resolve_project_path(args.mapping)
    output_path = resolve_project_path(args.output)
    report_path = resolve_project_path(args.report)

    if not mapping_path.exists():
        raise FileNotFoundError(f"File mapping tidak ditemukan: {mapping_path}")

    checks = refine_recommendations(
        input_path=input_path,
        mapping_path=mapping_path,
        output_path=output_path,
        report_path=report_path,
    )

    print("Recommendation text refinement selesai.")
    print(f"Input digunakan: {input_path}")
    print(f"Mapping digunakan: {mapping_path}")
    print(f"Output dibuat: {output_path}")
    print(f"Report dibuat: {report_path}")

    for key, value in checks.items():
        print(f"{key}: {value}")


if __name__ == "__main__":
    main()
