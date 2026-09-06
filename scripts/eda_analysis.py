"""Exploratory Data Analysis (EDA) for Architectural AI Assistant Datasets."""
import os
import json
import re
from pathlib import Path
from collections import Counter
import pymupdf  # PyMuPDF
from PIL import Image
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Headless backend
import matplotlib.pyplot as plt

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
SCENARIOS_DIR = DATA_DIR / "scenarios"
OUTPUT_DIR = DATA_DIR / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def analyze_pdf(pdf_path: Path):
    """Performs deep text and structure EDA on the 2010 ADA design standards PDF."""
    print(f"\n--- 1. Regulatory Document EDA: {pdf_path.name} ---")
    doc = pymupdf.open(str(pdf_path))
    total_pages = len(doc)
    page_word_counts = []
    page_char_counts = []
    empty_pages = 0

    # Key architectural and compliance terms
    search_terms = [
        "clear width", "walking surface", "door", "corridor", "hallway",
        "ramp", "stair", "turning space", "restroom", "kitchen",
        "reach range", "grab bar", "clearance", "elevation", "slope"
    ]
    term_counts = Counter()
    term_page_coverage = {term: 0 for term in search_terms}

    chapters = []
    for idx in range(total_pages):
        page = doc[idx]
        text = page.get_text()
        words = text.split()
        word_count = len(words)
        char_count = len(text)

        page_word_counts.append(word_count)
        page_char_counts.append(char_count)

        if word_count == 0:
            empty_pages += 1

        # Check for chapter/section headings
        headers = re.findall(r"(CHAPTER\s+\d+|SECTION\s+\d+|[0-9]{3}\.[0-9]+)", text, re.IGNORECASE)
        if headers:
            chapters.extend(headers)

        # Keyword frequencies
        text_lower = text.lower()
        for term in search_terms:
            count = text_lower.count(term)
            if count > 0:
                term_counts[term] += count
                term_page_coverage[term] += 1

    doc.close()

    df_pages = pd.DataFrame({
        "page": range(1, total_pages + 1),
        "word_count": page_word_counts,
        "char_count": page_char_counts
    })

    print(f"Total Pages: {total_pages}")
    print(f"Non-empty Pages: {total_pages - empty_pages}")
    print(f"Total Words: {df_pages['word_count'].sum():,}")
    print(f"Mean Words / Page: {df_pages['word_count'].mean():.1f}")
    print(f"Median Words / Page: {df_pages['word_count'].median():.1f}")
    print(f"Max Words on Single Page: {df_pages['word_count'].max()}")

    print("\nTop Compliance Term Frequencies:")
    for term, cnt in term_counts.most_common():
        cov = term_page_coverage[term]
        pct = (cov / total_pages) * 100
        print(f"  - '{term}': {cnt} occurrences across {cov} pages ({pct:.1f}% of doc)")

    return df_pages, term_counts, term_page_coverage


def analyze_floor_plans(scenarios_dir: Path, raw_dir: Path):
    """Analyzes architectural floor plan images and structured representations."""
    print("\n--- 2. Floor Plan Dataset EDA ---")
    image_files = sorted([f for f in scenarios_dir.iterdir() if f.suffix.lower() == ".png"])

    img_records = []
    for img_path in image_files:
        with Image.open(img_path) as img:
            w, h = img.size
            aspect = w / h
            mode = img.mode
            img_format = img.format
            file_size_kb = img_path.stat().st_size / 1024
            img_records.append({
                "filename": img_path.name,
                "width": w,
                "height": h,
                "aspect_ratio": round(aspect, 2),
                "mode": mode,
                "format": img_format,
                "size_kb": round(file_size_kb, 1)
            })

    df_imgs = pd.DataFrame(img_records)
    print(df_imgs.to_string(index=False))

    # Analyze structured JSON
    json_path = raw_dir / "cubicasa_sample_1.json"
    json_summary = {}
    if json_path.exists():
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        rooms = data.get("rooms", [])
        walls = data.get("walls", [])

        print(f"\nSample Structured Plan: {json_path.name}")
        print(f"Project ID: {data.get('project_id')}")
        print(f"Total Rooms Defined: {len(rooms)}")
        print(f"Total Walls Defined: {len(walls)}")
        for r in rooms:
            dims = r.get("dimensions", {})
            print(f"  - Room '{r.get('id')}' ({r.get('type')}): {dims.get('width_ft')}ft x {dims.get('length_ft')}ft ({dims.get('area_sqft')} sqft), Doors: {r.get('doors')}, Windows: {r.get('windows')}")
        json_summary = {"rooms": rooms, "walls": walls}

    return df_imgs, json_summary


def generate_eda_visualizations(df_pages, term_counts, df_imgs, output_path: Path):
    """Generates a composite EDA dashboard visualization."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle("Exploratory Data Analysis: Architectural AI Dataset", fontsize=16, fontweight="bold")

    # 1. Page Word Count Distribution
    axes[0, 0].hist(df_pages["word_count"], bins=30, color="#2b5c8f", edgecolor="black", alpha=0.8)
    axes[0, 0].set_title("Distribution of Words per Page (ADA 2010)", fontsize=12)
    axes[0, 0].set_xlabel("Word Count")
    axes[0, 0].set_ylabel("Number of Pages")
    axes[0, 0].axvline(df_pages["word_count"].mean(), color="red", linestyle="--", label=f"Mean: {df_pages['word_count'].mean():.0f}")
    axes[0, 0].legend()

    # 2. Word Count across Document Pages (Chronological/Sequential)
    axes[0, 1].plot(df_pages["page"], df_pages["word_count"], color="#1f77b4", linewidth=1.2)
    axes[0, 1].set_title("Word Count Across Document Progression", fontsize=12)
    axes[0, 1].set_xlabel("Page Number")
    axes[0, 1].set_ylabel("Words")
    axes[0, 1].grid(True, alpha=0.3)

    # 3. Top Compliance Keywords Frequency
    terms, counts = zip(*term_counts.most_common(10))
    y_pos = range(len(terms))
    axes[1, 0].barh(y_pos, counts, color="#2ca02c", edgecolor="black", alpha=0.85)
    axes[1, 0].set_yticks(y_pos)
    axes[1, 0].set_yticklabels(terms)
    axes[1, 0].invert_yaxis()
    axes[1, 0].set_title("Top 10 Regulatory & Accessibility Keywords", fontsize=12)
    axes[1, 0].set_xlabel("Occurrences")

    # 4. Floor Plan Image Resolutions
    scatter = axes[1, 1].scatter(df_imgs["width"], df_imgs["height"], c=df_imgs["size_kb"], cmap="viridis", s=180, edgecolors="black")
    for _, row in df_imgs.iterrows():
        axes[1, 1].annotate(row["filename"], (row["width"] + 10, row["height"] + 10), fontsize=9)
    axes[1, 1].set_title("Floor Plan Resolutions (Width vs Height)", fontsize=12)
    axes[1, 1].set_xlabel("Width (px)")
    axes[1, 1].set_ylabel("Height (px)")
    cbar = plt.colorbar(scatter, ax=axes[1, 1])
    cbar.set_label("File Size (KB)")

    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.savefig(output_path, dpi=200)
    plt.close()
    print(f"\nSaved EDA composite visualization to: {output_path}")


def main():
    pdf_path = RAW_DIR / "2010-design-standards.pdf"
    df_pages, term_counts, term_coverage = analyze_pdf(pdf_path)
    df_imgs, json_summary = analyze_floor_plans(SCENARIOS_DIR, RAW_DIR)

    plot_path = OUTPUT_DIR / "eda_summary.png"
    generate_eda_visualizations(df_pages, term_counts, df_imgs, plot_path)

    # Save summary metrics JSON for reporting
    eda_stats = {
        "pdf_total_pages": len(df_pages),
        "pdf_total_words": int(df_pages["word_count"].sum()),
        "pdf_mean_words_per_page": round(float(df_pages["word_count"].mean()), 1),
        "pdf_top_terms": dict(term_counts.most_common(12)),
        "floor_plans_count": len(df_imgs),
        "floor_plan_resolutions": df_imgs.to_dict(orient="records"),
    }
    with open(OUTPUT_DIR / "eda_stats.json", "w", encoding="utf-8") as f:
        json.dump(eda_stats, f, indent=2)

    print("\nEDA completed successfully.")


if __name__ == "__main__":
    main()
