import cairosvg
from pathlib import Path

WIDTH = 1080
HEIGHT = 1920

BLACK = "#000000"
WHITE = "#FFFFFF"


def create_svg():
    return f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         width="{WIDTH}"
         height="{HEIGHT}"
         viewBox="0 0 1080 1920">

        <rect width="1080" height="1920" fill="{WHITE}"/>

        <!-- Bench -->
        <line x1="250" y1="950" x2="830" y2="950"
              stroke="{BLACK}" stroke-width="12"
              stroke-linecap="round"/>

        <line x1="320" y1="950" x2="320" y2="1250"
              stroke="{BLACK}" stroke-width="12"/>

        <line x1="760" y1="950" x2="760" y2="1250"
              stroke="{BLACK}" stroke-width="12"/>

        <!-- Head -->
        <circle cx="540" cy="510" r="85"
                fill="none" stroke="{BLACK}"
                stroke-width="14"/>

        <!-- Body: slightly hunched -->
        <path d="M540 595 Q510 720 540 880"
              stroke="{BLACK}" stroke-width="16"
              fill="none" stroke-linecap="round"/>

        <!-- Left arm -->
        <path d="M530 670 L420 790 L440 900"
              stroke="{BLACK}" stroke-width="14"
              fill="none" stroke-linecap="round"
              stroke-linejoin="round"/>

        <!-- Right arm -->
        <path d="M550 670 L660 790 L640 900"
              stroke="{BLACK}" stroke-width="14"
              fill="none" stroke-linecap="round"
              stroke-linejoin="round"/>

        <!-- Left leg -->
        <path d="M540 880 L390 940 L390 1100"
              stroke="{BLACK}" stroke-width="16"
              fill="none" stroke-linecap="round"
              stroke-linejoin="round"/>

        <!-- Right leg -->
        <path d="M540 880 L690 940 L690 1100"
              stroke="{BLACK}" stroke-width="16"
              fill="none" stroke-linecap="round"
              stroke-linejoin="round"/>

        <!-- Feet -->
        <path d="M390 1100 L470 1100"
              stroke="{BLACK}" stroke-width="16"
              stroke-linecap="round"/>

        <path d="M690 1100 L770 1100"
              stroke="{BLACK}" stroke-width="16"
              stroke-linecap="round"/>

        <!-- Hands -->
        <circle cx="440" cy="900" r="12" fill="{BLACK}"/>
        <circle cx="640" cy="900" r="12" fill="{BLACK}"/>

    </svg>
    """


def generate_image(output_path):
    svg_content = create_svg()

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    cairosvg.svg2png(
        bytestring=svg_content.encode("utf-8"),
        write_to=str(output_path),
        output_width=WIDTH,
        output_height=HEIGHT
    )

    print(f"Illustration saved to: {output_path}")


if __name__ == "__main__":
    generate_image("output/video_001/images/scene_01.png")