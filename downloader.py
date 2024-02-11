from pathlib import Path

import requests
from bs4 import BeautifulSoup


def main():

    legs = {
        17: [2013, 2014, 2015, 2016, 2017, 2018],
        18: [2018, 2019, 2020, 2021, 2022],
    }

    for leg, years in legs.items():

        output_dir = Path(f"leg{leg}")
        output_dir.mkdir(parents=True, exist_ok=True)
        for year in years:
            for month in range(1, 13):
                base_link = (
                    f"https://www.camera.it/leg{leg}/207?annomese={year},{month}"
                )
                base_page = requests.get(base_link)
                soup = BeautifulSoup(base_page.text, features="html.parser")
                for result in soup.find_all("a", {"class": "eleres_epub link_esterno"}):
                    epub_link = f"https:{result.attrs['href']}"
                    filename = epub_link.split("/")[-1]

                    request = requests.get(epub_link, stream=True)
                    if request.ok:
                        with Path(f"{output_dir}/{filename}").open("wb") as ofile:
                            content = request.content
                            ofile.write(content)

                    else:
                        print(f"error:\t{epub_link}")


if __name__ == "__main__":
    main()
