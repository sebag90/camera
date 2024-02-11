import argparse
from io import BytesIO
from pathlib import Path
import re
import zipfile

from bs4 import BeautifulSoup


def get_html(path):
    data = path.read_bytes()
    zf = zipfile.ZipFile(BytesIO(data), "r")
    for fileinfo in zf.infolist():
        if "stenografico" in fileinfo.filename:
            return zf.read(fileinfo).decode()


def main(args):
    for i, file in enumerate(Path(args.input).iterdir()):
        # parse epub file
        data = get_html(file)
        soup = BeautifulSoup(data, features="lxml")
        steno = soup.find("div", {"id": "stenografico"})

        # initialise temporary variables
        current_speaker = None
        temp = ""
        president = ""

        cleaning_regex = re.compile(
            # match spaces or punctuation at the beginning of a text (except parenthesis)
            r"^[^a-zA-Z0-9\(\)]+"
        )

        # create output directory and file
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        outputfile = Path(f"{output_dir}/{file.stem}.txt")

        with outputfile.open("w", encoding="utf-8") as ofile:
            # print header
            print("\t".join(["speaker", "role", "text", "extra"]), file=ofile)

            for element in steno.find_all("p"):
                try:
                    element_type = element.attrs["class"].pop()
                except:
                    # leg17
                    element_type = "interventoVirtuale"

                if element_type == "presidenza":
                    # extract name of president
                    president_line = re.sub(r"\([^)]+\)", "", element.text)
                    split_text = president_line.strip().split()
                    index = (
                        3 if split_text[3] not in {"PROVVISORIO", "PROVVISORIA"} else 4
                    )
                    president = " ".join(split_text[index:])

                if element_type == "intervento":
                    # write down this temp line
                    if current_speaker is not None:
                        speaker, name = current_speaker

                        if speaker == "PRESIDENTE":
                            speaker = president
                            role = "PRESIDENTE"

                        print(
                            "\t".join(
                                [
                                    speaker,
                                    # match any spaces or punctuation at the end
                                    re.sub(r"\s?[\.|,]\s?$", "", role).strip(),
                                    temp.strip(),
                                    "",
                                ]
                            ),
                            file=ofile,
                        )

                        temp = ""

                    # extract speaker name
                    try:
                        speaker = element.a.text.strip()
                    except:
                        speaker = element.text.strip().split(".")[0]

                    # string cleaning
                    complete_line = element.text
                    complete_line = complete_line.replace(speaker, "").strip()
                    complete_line = re.sub(cleaning_regex, "", complete_line)

                    # determine role of this person
                    role = ""
                    if element.em is not None:
                        possible_role = element.em.text.strip()

                        if complete_line.startswith(possible_role):
                            role = possible_role

                    if element.span is not None:
                        role = element.span.text.strip()

                    # clean again the string
                    current_speaker = (speaker, role)
                    complete_line = complete_line.replace(speaker, "").strip()
                    complete_line = complete_line.replace(role, "").strip()
                    complete_line = re.sub(cleaning_regex, "", complete_line)

                    if complete_line.startswith("("):
                        complete_line = re.sub(r"\(\)[.|,]", "", complete_line)

                    # normalize spaces
                    complete_line = re.sub(r"\s+", " ", complete_line)
                    temp += f"{complete_line.strip()} "

                elif element_type == "interventoVirtuale":
                    # normalize spaces
                    text = re.sub(r"\s+", " ", element.text)
                    temp += f"{text.strip()} "

                else:
                    # normalize spaces
                    to_print = re.sub(r"\s+", " ", element.text)
                    print("\t".join(["", "", "", to_print.strip()]), file=ofile)

        if i % 100 == 0:
            print(i, end="", flush=True)

        elif i % 10 == 0:
            print(".", end="", flush=True)

    print("Processing complete")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("input")
    parser.add_argument("output")
    args = parser.parse_args()
    main(args)
