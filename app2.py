import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="3D Lithography Simulator", layout="wide")

# -------------------------------
# Functions
# -------------------------------

def rpm_from_thickness(thickness, material):
    if material == "AZ1505":
        return int(3000 * (500 / thickness))
    elif material == "PMMA":
        return int(4000 * (300 / thickness))

def generate_mask(mask_type, size=100):
    mask = np.zeros((size, size))

    if mask_type == "Lines":
        mask[:, ::10] = 1
    elif mask_type == "Dots":
        for i in range(0, size, 15):
            for j in range(0, size, 15):
                mask[i:i+3, j:j+3] = 1
    elif mask_type == "Square":
        mask[30:70, 30:70] = 1

    return mask

def create_3d_plot(sio2, resist, developed=None):
    size = sio2.shape[0]
    x = np.linspace(0, 1, size)
    y = np.linspace(0, 1, size)
    X, Y = np.meshgrid(x, y)

    fig = go.Figure()

    # SiO2 Layer
    fig.add_trace(go.Surface(
        z=sio2,
        x=X, y=Y,
        colorscale='Blues',
        showscale=False,
        opacity=0.9,
        name="SiO2"
    ))

    # Resist Layer
    fig.add_trace(go.Surface(
        z=sio2 + resist,
        x=X, y=Y,
        colorscale='Reds',
        showscale=False,
        opacity=0.8,
        name="Photoresist"
    ))

    # Developed Pattern
    if developed is not None:
        fig.add_trace(go.Surface(
            z=sio2 + developed,
            x=X, y=Y,
            colorscale='Greens',
            showscale=False,
            opacity=1.0,
            name="Developed"
        ))

    fig.update_layout(
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Height'
        ),
        height=700
    )

    return fig

# -------------------------------
# Sidebar
# -------------------------------

tab = st.sidebar.radio("Navigation", ["Simulation", "Theory"])

# -------------------------------
# THEORY
# -------------------------------

if tab == "Theory":
    st.title("Lithography Theory (3D View Enabled)")

    st.markdown("""
    This simulator visualizes lithography as stacked 3D layers:

    - **SiO₂ Layer** → Base dielectric
    - **Photoresist Layer** → Spin-coated polymer
    - **Exposure** → UV modifies solubility
    - **Development** → Removes selected regions

    The 3D model helps visualize:
    - Thickness variation
    - Pattern transfer
    - Surface topology after development
    """)

# -------------------------------
# SIMULATION
# -------------------------------

else:
    st.title("3D Lithography Simulator")

    size = 100

    # Step 1: SiO2
    st.header("Step 1: SiO₂ Deposition")
    sio2_thickness = st.slider("SiO₂ Thickness", 100, 1000, 300)

    sio2 = np.ones((size, size)) * sio2_thickness

    # Step 2: Resist
    st.header("Step 2: Photoresist")

    resist_type = st.selectbox("Resist", ["AZ1505", "PMMA"])
    thickness = st.slider("Resist Thickness", 100, 1000, 500)

    rpm = rpm_from_thickness(thickness, resist_type)
    st.write(f"Suggested RPM: **{rpm}**")

    resist = np.ones((size, size)) * thickness

    # Step 3: Mask
    st.header("Step 3: Mask & Exposure")

    mask_type = st.selectbox("Mask", ["Lines", "Dots", "Square"])
    polarity = st.radio("Polarity", ["Positive", "Negative"])

    mask = generate_mask(mask_type, size)

    if polarity == "Positive":
        exposed = mask
    else:
        exposed = 1 - mask

    # Step 4: Development
    st.header("Step 4: Development")

    developed = resist.copy()

    if polarity == "Positive":
        developed[exposed == 1] = 0
    else:
        developed[exposed == 0] = 0

    # 3D Visualization
    st.header("3D Visualization")

    fig = create_3d_plot(sio2, resist, developed)
    st.plotly_chart(fig, use_container_width=True)

    st.success("3D Pattern Generated Successfully!")