#!/usr/bin/env python3
import sys

from app.csv_to_html import main, write_html


if __name__ == "__main__":
    html, out_path = main(sys.argv[1])
    write_html(html, out_path)
