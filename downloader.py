import argparse
from pathlib import Path

import requests
from bs4 import BeautifulSoup


def main(args):
    legs = {
        17: [2013, 2014, 2015, 2016, 2017, 2018],
        18: [2018, 2019, 2020, 2021, 2022],
    }

    for leg, years in legs.items():
        # create directories
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)

        # iterate over years and months
        for year in years:
            for month in range(1, 13):
                base_link = (
                    f"https://www.camera.it/leg{leg}/207?annomese={year},{month}"
                )
                base_page = requests.get(base_link)

                # find epub download links
                soup = BeautifulSoup(base_page.text, features="html.parser")
                for result in soup.find_all("a", {"class": "eleres_epub link_esterno"}):
                    epub_link = f"https:{result.attrs['href']}"
                    filename = epub_link.split("/")[-1]

                    # check if download link is valid
                    request = requests.get(epub_link, stream=True)
                    if request.ok:
                        # download epub
                        with Path(f"{output_dir}/{filename}").open("wb") as ofile:
                            content = request.content
                            ofile.write(content)

                    else:
                        print(f"error:\t{epub_link}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("output")
    args = parser.parse_args()
    main(args)
