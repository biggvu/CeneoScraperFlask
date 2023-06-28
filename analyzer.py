import os
import pandas as pd
import json
import numpy as np
from matplotlib import pyplot as plt
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    opinions_dir = "./opinions"
    product_codes = [filename.split(".")[0] for filename in os.listdir(opinions_dir)]
    return render_template('index.html', product_codes=product_codes)

@app.route('/product/<product_code>')
def product_details(product_code):
    opinions_file = f"./opinions/{product_code}.json"
    plots_dir = "./plots"
    stats_dir = "./stats"

    opinions = pd.read_json(opinions_file)
    opinions.score = opinions.score.map(lambda x: x.split("/")[0].replace(",", ".")).astype(float)

    opinions_count = opinions.shape[0]
    pros_count = int(opinions.pros.astype(bool).sum())
    cons_count = int(opinions.cons.astype(bool).sum())
    average_score = opinions.score.mean()

    stats = {
        "opinions_count": opinions_count,
        "pros_count": pros_count,
        "cons_count": cons_count,
        "average_score": average_score
    }

    if not os.path.exists(plots_dir):
        os.mkdir(plots_dir)

    score = opinions.score.value_counts().reindex(list(np.arange(0, 5.5, 0.5)), fill_value=0)
    score.plot.bar()
    plt.savefig(f"{plots_dir}/{product_code}_score.png")
    plt.close()

    recommendation = opinions.recommendation.value_counts(dropna=False)
    recommendation.plot.pie()
    plt.savefig(f"{plots_dir}/{product_code}_recommendation.png")
    plt.close()

    if not os.path.exists(stats_dir):
        os.mkdir(stats_dir)

    stats["score"] = score.to_dict()
    stats["recommendation"] = recommendation.to_dict()

    stats_file = f"{stats_dir}/{product_code}.json"
    with open(stats_file, "w", encoding="UTF-8") as jf:
        json.dump(stats, jf, indent=4, ensure_ascii=False)

    return render_template('product.html', product_code=product_code, stats=stats)

if __name__ == '__main__':
    app.run()
