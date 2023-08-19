from collections import Counter
import cv2
import exif
import json
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
from pathlib import Path
import seaborn as sns
from sklearn.cluster import KMeans

base_path = Path(os.getcwd())
OUTPUT_PATH =  base_path / "output"
IMAGE_PATH = base_path / "images"


def color_analysis(img, file):
    clf = KMeans(n_clusters=5)
    color_labels = clf.fit_predict(img)
    center_colors = clf.cluster_centers_
    counts = Counter(color_labels)
    ordered_colors = [center_colors[i] for i in counts.keys()]
    hex_colors = [rgb_to_hex(ordered_colors[i]) for i in counts.keys()]
    plt.figure(figsize=(12, 8))
    plt.pie(
        counts.values(), 
        labels=hex_colors, 
        colors=hex_colors, 
        autopct="%1.1f%%",
    )
    file_path = OUTPUT_PATH / f"{file}_analysis.png"
    plt.savefig(file_path)
    plt.close()


def resize_image(raw_img):
    modified_img = cv2.resize(
        raw_img, 
        (900, 600), 
        interpolation=cv2.INTER_AREA
    )
    
    return modified_img.reshape(
        modified_img.shape[0]*modified_img.shape[1], 
        3
    )


def rgb_to_hex(rgb_color):
    hex_color = "#"
    for i in rgb_color:
        i = int(i)
        hex_color += ("{:02x}".format(i))
    
    return hex_color


def run_metrics(file, exif_output, cumulative_cv2):
    exif_data = dict()
    file_path = IMAGE_PATH / file
    with open(file_path, "rb") as image_file:
        cv2_data = cv2.imread(str(file_path))
        cv2_data = cv2.cvtColor(cv2_data, cv2.COLOR_BGR2RGB)
        modified_image = resize_image(cv2_data)
        color_analysis(modified_image, file)
        cumulative_cv2 = np.append(cumulative_cv2, modified_image)
        my_image = exif.Image(image_file)
        exif_output[file] = {
            "Focal Length": my_image.focal_length,
            "Exposure Time": my_image.exposure_time,
            "ISO": my_image.photographic_sensitivity,
            "F/Number": my_image.f_number,
            "Lens Model": my_image.lens_model.replace("/",""),
        }
        
    return exif_output, cumulative_cv2


def chart_output(json_path):
    with open(json_path, "r") as json_file:
        df = pd.read_json(json_file)
    df2 = df.T
    sns.relplot(
        data=df2, 
        x="Focal Length",
        y="Exposure Time", 
        hue="ISO", 
        size="F/Number",
        style="Lens Model",
        palette="cool"
    )
    dotplot_path = OUTPUT_PATH / "dotplot.png"
    plt.savefig(
        dotplot_path,
        bbox_inches ="tight",
        dpi=300,
        pad_inches = 1,
        transparent = False,
        orientation ="landscape"
    )


def main():
    exif_output = dict()
    init_cumulative_cv2 = np.zeros((540000,3), np.uint8)
    cumulative_cv2 = init_cumulative_cv2
    for file in os.listdir(IMAGE_PATH):
        print(f"Working on {file}")
        exif_output, cumulative_cv2 = run_metrics(
            file, 
            exif_output, 
            cumulative_cv2
        )
    # cumulative_cv2 = cumulative_cv2.reshape(-1, 1)
    # color_analysis(cumulative_cv2, "cumulative")
    json_path = OUTPUT_PATH / "metric.json"
    with open(json_path, "w") as json_file:
        json.dump(exif_output, json_file)
    chart_output(json_path)


if __name__ == "__main__":
    main()
