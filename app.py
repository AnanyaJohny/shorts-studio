import streamlit as st
from pathlib import Path
import subprocess

from src.script_generator.generator import generate_script
from src.scene_planner.planner import generate_scene_plan
from src.scene_tester.validator import validate_scenes
from src.scene_tester.reviewer import review_scenes
from src.project_manager import create_project


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Shorts Studio",
    page_icon="🎬",
    layout="wide"
)

st.title("🎬 Shorts Studio")
st.caption("Your AI-powered YouTube Shorts production studio.")

st.divider()


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

defaults = {
    "script": None,
    "storyboard": None,
    "ai_review": None,
    "python_issues": [],
    "project_id": None,
    "pipeline_completed": False,
    "video_path": None,
    "video_error": None
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# --------------------------------------------------
# GENERATE SHORT
# --------------------------------------------------

st.header("Create a new Short")

topic = st.text_input(
    "What should your next Short be about?",
    placeholder="e.g. Why do we overthink conversations?"
)

if st.button("🚀 Generate Short", type="primary"):

    if not topic.strip():
        st.warning("Please enter a topic first.")

    else:
        try:
            # Reset previous project state
            st.session_state.script = None
            st.session_state.storyboard = None
            st.session_state.ai_review = None
            st.session_state.python_issues = []
            st.session_state.project_id = None
            st.session_state.pipeline_completed = False
            st.session_state.video_path = None
            st.session_state.video_error = None

            # STEP 1: Generate script
            with st.spinner("Step 1/4: Generating script..."):
                script = generate_script(topic)

            # STEP 2: Generate storyboard
            with st.spinner("Step 2/4: Creating storyboard..."):
                storyboard = generate_scene_plan(
                    script.full_script
                )

            # STEP 3: Python validation
            with st.spinner("Step 3/4: Validating scenes..."):
                python_issues = validate_scenes(
                    script.full_script,
                    storyboard
                )

            # STEP 4: AI visual review
            with st.spinner("Step 4/4: Reviewing visuals..."):
                ai_review = review_scenes(
                    script.full_script,
                    storyboard.model_dump()
                )

            # Store results
            st.session_state.script = script.model_dump()
            st.session_state.storyboard = storyboard.model_dump()
            st.session_state.ai_review = ai_review.model_dump()
            st.session_state.python_issues = python_issues

            # Determine approval
            critical_issues = [
                issue for issue in ai_review.issues
                if str(issue.severity).upper().endswith("CRITICAL")
            ]

            passed = (
                not python_issues
                and not critical_issues
            )

            if passed:
                video_id = create_project(
                    script.model_dump(),
                    storyboard.model_dump()
                )

                st.session_state.project_id = video_id
                st.session_state.pipeline_completed = True

        except Exception as e:
            st.error(f"Pipeline failed: {e}")


# --------------------------------------------------
# PRODUCTION WORKSPACE
# --------------------------------------------------

if st.session_state.script:

    st.divider()
    st.header("Production Workspace")

    if st.session_state.pipeline_completed:

        st.success("Pipeline completed successfully!")

        st.info(
            f"Project ID: {st.session_state.project_id}"
        )

    else:
        st.error("Pipeline did not pass validation.")

    # ----------------------------------------------
    # GENERATED SCRIPT
    # ----------------------------------------------

    st.subheader("📝 Generated Script")

    script = st.session_state.script

    st.write(f"**Title:** {script['title']}")
    st.write(f"**Topic:** {script['topic']}")

    st.markdown("**Full Narration**")
    st.write(script["full_script"])

    st.markdown("**Takeaway**")
    st.write(script["takeaway"])

    # ----------------------------------------------
    # QUALITY REVIEW
    # ----------------------------------------------

    st.divider()
    st.subheader("🔍 Quality Review")

    if st.session_state.python_issues:

        st.error("Python validation failed.")

        for issue in st.session_state.python_issues:
            st.write(f"- {issue}")

    else:
        st.success("Python validation passed.")

    ai_review = st.session_state.ai_review

    if ai_review:

        if ai_review["passed"]:
            st.success("AI visual review passed.")
        else:
            st.warning("AI visual review identified issues.")

        with st.expander("View AI review details"):

            st.write(ai_review["overall_feedback"])

            for issue in ai_review["issues"]:

                st.markdown(
                    f"**Scene {issue['scene_number']} — "
                    f"{issue['severity']}**"
                )

                st.write(issue["issue"])
                st.write(issue["explanation"])

                st.caption(
                    f"Suggested fix: {issue['suggested_fix']}"
                )

    # ----------------------------------------------
    # MASTER ILLUSTRATION PROMPT
    # ----------------------------------------------

    MASTER_IMAGE_PROMPT = """
Create minimalist, hand-drawn black stickman illustrations
on a pure white background.

VISUAL STYLE:

- 9:16 vertical composition.
- Simple black line art.
- One consistent stickman character throughout all images.
- Round head, simple facial features, thin black limbs.
- Clean, smooth strokes with consistent line thickness.
- Minimalist editorial illustration aesthetic.
- Large amounts of white negative space.
- Use simple visual metaphors where appropriate.
- Keep the main character centred and clearly visible.

STRICT RESTRICTIONS:

- No colours other than black and white.
- No text, letters, numbers, typography or captions.
- No watermarks.
- No realistic humans or photographic elements.
- No unnecessary decorative elements.
- Do not change the character's appearance between scenes.
"""

    # ----------------------------------------------
    # STORYBOARD AND IMAGE UPLOADS
    # ----------------------------------------------

    st.divider()
    st.header("🎨 Storyboard")

    st.caption(
        "Copy the complete image prompt for each scene, "
        "generate your illustration, and upload it below."
    )

    st.subheader("📋 Master Illustration Prompt")

    st.code(
        MASTER_IMAGE_PROMPT,
        language=None
    )

    storyboard = st.session_state.storyboard
    project_id = st.session_state.project_id

    if storyboard:

        if project_id:

            image_dir = (
                Path("output")
                / project_id
                / "images"
            )

            image_dir.mkdir(
                parents=True,
                exist_ok=True
            )

            for scene in storyboard["scenes"]:

                scene_number = scene["scene_number"]

                image_name = f"scene_{scene_number:02d}"

                # Combine master prompt and scene description
                complete_prompt = (
                    MASTER_IMAGE_PROMPT
                    + "\n\nSCENE-SPECIFIC DESCRIPTION:\n"
                    + scene["visual_description"]
                )

                with st.container(border=True):

                    st.subheader(f"Scene {scene_number}")

                    st.markdown("**Narration**")
                    st.write(scene["narration"])

                    st.markdown("**Visual Description**")
                    st.write(scene["visual_description"])

                    st.markdown(
                        "**Complete Image Generation Prompt**"
                    )

                    st.code(
                        complete_prompt,
                        language=None
                    )

                    # Image uploader
                    uploaded_file = st.file_uploader(
                        f"Upload image for Scene {scene_number}",
                        type=["png", "jpg", "jpeg", "webp"],
                        key=(
                            f"image_upload_"
                            f"{project_id}_{scene_number}"
                        )
                    )

                    # Save uploaded image
                    if uploaded_file:

                        extension = Path(
                            uploaded_file.name
                        ).suffix.lower()

                        # Keep exactly one image file per scene.
                        for old_image in image_dir.glob(f"{image_name}.*"):
                            old_image.unlink()

                        image_path = (
                            image_dir
                            / f"{image_name}{extension}"
                        )

                        image_path.write_bytes(
                            uploaded_file.getvalue()
                        )

                        st.success(
                            "Image uploaded successfully!"
                        )

                    # Display uploaded image
                    existing_images = list(
                        image_dir.glob(f"{image_name}.*")
                    )

                    if existing_images:

                        st.image(
                            str(existing_images[0]),
                            caption=f"Scene {scene_number}",
                            width=300
                        )

        else:

            st.warning(
                "Images can be uploaded after the project "
                "passes validation."
            )


# --------------------------------------------------
# VOICEOVER, SUBTITLES AND VIDEO RENDERING
# --------------------------------------------------

if st.session_state.pipeline_completed and st.session_state.project_id:

    st.divider()
    st.header("🎙️ Voiceover & Final Video")

    project_id = st.session_state.project_id
    project_dir = Path("output") / project_id
    expected_scenes = st.session_state.storyboard["scenes"]

    missing_images = []
    for scene in expected_scenes:
        number = scene["scene_number"]
        matches = [
            path for path in (project_dir / "images").glob(f"scene_{number:02d}.*")
            if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp"}
        ]
        if not matches:
            missing_images.append(number)

    if missing_images:
        st.warning(
            "Upload all scene images before rendering. "
            f"Missing scenes: {', '.join(map(str, missing_images))}"
        )
    else:
        st.success("All scene images are uploaded.")

        if st.button("🎬 Generate Video", type="primary"):
            voice_python = Path("voice_env/bin/python")

            if not voice_python.exists():
                st.error(
                    "Could not find voice_env/bin/python. "
                    "Make sure the voice_env folder is in your project root."
                )
            else:
                with st.spinner(
                    "Generating voiceover, transcribing speech, "
                    "creating subtitles and rendering your video. "
                    "This may take a few minutes..."
                ):
                    try:
                        result = subprocess.run(
                            [
                                str(voice_python),
                                "src/video_renderer/pipeline.py",
                                "--project-id",
                                project_id
                            ],
                            capture_output=True,
                            text=True,
                            check=True
                        )

                        video_path = project_dir / "final_video.mp4"
                        if not video_path.exists():
                            raise FileNotFoundError(
                                "Render process finished but final_video.mp4 was not found."
                            )

                        st.session_state.video_path = str(video_path)
                        st.session_state.video_error = None

                    except subprocess.CalledProcessError as error:
                        details = error.stderr or error.stdout or str(error)
                        st.session_state.video_error = details[-12000:]
                    except Exception as error:
                        st.session_state.video_error = str(error)

        if st.session_state.video_error:
            st.error("Video generation failed.")
            with st.expander("View error details", expanded=True):
                st.code(st.session_state.video_error)

        video_path = Path(st.session_state.video_path) if st.session_state.video_path else (
            project_dir / "final_video.mp4"
        )

        if video_path.exists():
            st.success("Your Short is ready!")
            st.video(str(video_path), width=360)

            with video_path.open("rb") as video_file:
                st.download_button(
                    label="⬇️ Download final video",
                    data=video_file,
                    file_name=f"{project_id}.mp4",
                    mime="video/mp4",
                    type="primary"
                )
