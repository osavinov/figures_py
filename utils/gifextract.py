import os
from typing import Union, Dict
from PIL import Image

main_dir: Union[str, bytes] = os.path.split(os.path.abspath(__file__))[0]


def analyse_image(path) -> Dict:
    im = Image.open(path)
    results = {"size": im.size, "mode": "full"}
    try:
        while True:
            if im.tile:
                tile = im.tile[0]
                update_region = tile[1]
                update_region_dimensions = update_region[2:]
                if update_region_dimensions != im.size:
                    results["mode"] = "partial"
                    break
            im.seek(im.tell() + 1)
    except EOFError:
        pass
    return results


def process_image(source_path: str, dest_folder: str):
    mode = analyse_image(source_path)["mode"]
    im = Image.open(source_path)

    image_counter = 0
    palette = im.getpalette()
    last_frame = im.convert("RGBA")

    try:
        while True:
            print(f"saving {source_path} ({mode}) frame {image_counter}, {im.size} {im.tile}")

            if not im.getpalette():
                im.putpalette(palette)

            new_frame = Image.new("RGBA", im.size)

            if mode == "partial":
                new_frame.paste(last_frame)

            new_frame.paste(im, (0, 0), im.convert("RGBA"))
            file_name_root: str = "".join(os.path.basename(source_path).split(".")[:-1])
            file_name: str = f"{file_name_root}-{image_counter}.png"
            new_frame.save(os.path.join(dest_folder, file_name), "PNG")

            image_counter += 1
            last_frame = new_frame
            im.seek(im.tell() + 1)
    except EOFError:
        pass


def main():
    process_image(os.path.join(main_dir, "../data", "background.gif"), os.path.join(main_dir, "../data", "bottle"))


if __name__ == "__main__":
    main()
