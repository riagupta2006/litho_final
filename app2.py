import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

# 1. Page Configuration
st.set_page_config(page_title="Virtual Lithography Lab", layout="wide")

# Constants
RESIST_CONSTANTS = {"AZ 1505": 31.62}

# Initialize session state variables to track the wafer through the steps
if 'current_thickness' not in st.session_state:
    st.session_state.current_thickness = 0.0
if 'selected_resist' not in st.session_state:
    st.session_state.selected_resist = "AZ 1505"
if 'resist_status' not in st.session_state:
    st.session_state.resist_status = "Unbaked"

# --- MAIN VIRTUAL LAB LAYOUT ---
st.title("🔬 Virtual Lab: Maskless Photolithography Process")
st.markdown("Explore the deposition, exposure, and development of positive photoresists on a silicon substrate using a Direct Laser Writer.")

# Create the standard Virtual Lab Tabs
tab_aim, tab_theory, tab_procedure, tab_simulation, tab_quiz = st.tabs([
    "🎯 Aim", "📚 Theory", "📝 Procedure", "⚙️ Simulation", "🧠 Quiz"
])

# --- TAB 1: AIM ---
with tab_aim:
    st.header("Objective")
    st.markdown("""
    The aim of this virtual experiment is to:
    * Understand the empirical relationship between spin speed (RPM) and photoresist film thickness.
    * Simulate the thermal effects of the Soft Bake and Post-Bake processes on film densification and pattern fidelity.
    * Examine the usage of a Maskless Laserwriter (uMLA) for pattern exposure, specifically analyzing the impact of Dose and Defocus on the beam profile.
    * Simulate the chemical development of a positive photoresist to reveal the final trenched architecture.
    """)

# --- TAB 2: THEORY ---
with tab_theory:
    st.header("Theoretical Background")
    
    st.subheader("1. Spin Coating")
    st.markdown("""
    Spin coating is used to deposit uniform thin films onto flat substrates. 
    The final film thickness ($t$) depends heavily on the spin speed ($\\omega$ in RPM) and the viscosity of the photoresist. 
    For AZ 1505, this can be approximated using the inverse square root law:
    
    $t = \\frac{k}{\\sqrt{\\omega}}$
    
    Where $k$ is a resist-specific constant calibrated to yield ~0.5 µm at 4000 RPM.
    """)
    
    st.subheader("2. Maskless Exposure (Direct Write)")
    st.markdown("""
    Traditional photolithography uses a photomask to transfer patterns. Maskless lithography eliminates the need for physical masks, using a computer-controlled laser to write directly onto the photoresist.
    * **Exposure Dose ($mJ/cm^2$):** Must be carefully calibrated based on photoresist sensitivity and laser wavelength (365 nm).
    * **Defocus Control ($\\mu m$):** The laser beam's focal position significantly affects feature quality. Optimal focus produces sharp features, while positive or negative defocus increases the spot size and blurs the edges.
    """)
    
    st.subheader("3. Development & Baking")
    st.markdown("""
    * **Softbake:** Removes residual solvents. Recommended 90°C to 110°C.
    * **Development:** A chemical developer dissolves portions of the resist. For a positive resist like AZ 1505, the exposed resist is dissolved while the unexposed resist remains.
    * **Hardbake:** Hardens the photoresist for subsequent processes (e.g., etching). The temperature is higher than the softbake, typically 100°C to 110°C, but pushing it too high will cause thermal reflow (melting) of the patterned features.
    """)

# --- TAB 3: PROCEDURE ---
with tab_procedure:
    st.header("Experiment Instructions")
    st.markdown("""
    1. Navigate to the **Simulation** tab.
    2. **Step 1 (Spin Coating):** Set your RPM to achieve the desired thickness.
    3. **Step 2 (Soft Bake):** Evaporate the solvent. Ensure you stay within the 90°C-110°C process window to avoid degrading the resist.
    4. **Step 3 (Exposure):** Select a digital pattern. Adjust the dose and observe how modifying the **Defocus** parameter spreads the laser intensity profile.
    5. **Step 4 (Development):** Submerge the wafer in the developer. Aim for ~120 seconds to clear the exposed regions without eroding the unexposed walls.
    6. **Step 5 (Hardbake):** Apply a final thermal bake to harden the geometry. Watch the graph carefully to ensure you do not melt the trench walls!
    """)

# --- TAB 4: SIMULATION ---
with tab_simulation:
    st.sidebar.title("Lab Controls")
    resist_type = st.sidebar.selectbox("Select Photoresist:", list(RESIST_CONSTANTS.keys()))
    st.session_state.selected_resist = resist_type
    
    st.sidebar.markdown("---")
    
    # EXACT STRING MATCHES for the steps
    step = st.sidebar.radio(
        "Select Process Step:",
        [
            "1. Spin Coating", 
            "2. Soft Bake", 
            "3. Maskless Exposure", 
            "4. Development", 
            "5. Post-Bake (Hardbake)"
        ]
    )

    # --- Step 1 Logic ---
    if step == "1. Spin Coating":
        st.header("Step 1: Photoresist Spin Coating")
        
        rpm = st.sidebar.slider("Spin Speed (RPM)", min_value=500, max_value=5000, value=3000, step=100)
        
        k_val = RESIST_CONSTANTS[st.session_state.selected_resist]
        thickness_um = k_val / np.sqrt(rpm)
        st.session_state.current_thickness = thickness_um 
        st.session_state.resist_status = "Unbaked" 
        
        # Reset downstream variables if user re-spins
        if 'received_dose' in st.session_state: del st.session_state['received_dose']
        if 'developed_profile' in st.session_state: del st.session_state['developed_profile']
        
        col1, col2 = st.columns(2)
        col1.metric("Spin Speed", f"{rpm} RPM")
        col2.metric("Calculated Film Thickness", f"{thickness_um:.3f} µm")
            
        st.markdown("---")
        fig, ax = plt.subplots(figsize=(10, 4))
        x = np.linspace(0, 10, 500)
        
        ax.fill_between(x, 0, -2, color='#A9A9A9', label='Silicon Substrate')
        ax.fill_between(x, 0, thickness_um, color='#FF4500', alpha=0.7, label=f'AZ 1505 ({thickness_um:.2f} µm)')
        
        ax.set_ylim(-2.5, 4.0) 
        ax.set_xlim(0, 10)
        ax.set_ylabel("Thickness (µm)")
        ax.set_xticks([])
        ax.legend(loc="upper right")
        ax.grid(True, axis='y', linestyle='--', alpha=0.5)
        st.pyplot(fig)

    # --- Step 2 Logic ---
    elif step == "2. Soft Bake":
        st.header("Step 2: Soft Bake")
        
        if st.session_state.current_thickness == 0.0:
            st.warning("⚠️ Please execute Step 1 (Spin Coating) first!")
        else:
            temp = st.sidebar.slider("Temperature (°C)", min_value=70, max_value=150, value=100, step=5)
            time_sec = st.sidebar.slider("Time (seconds)", min_value=30, max_value=120, value=90, step=10)
            
            pr_color = '#FF4500' 
            shrinkage_factor = 1.0
            
            if temp < 90:
                st.session_state.resist_status = "Underbaked"
                shrinkage_factor = 0.98 
                pr_color = '#FFA07A' 
            elif 90 <= temp <= 100:
                st.session_state.resist_status = "Optimal"
                shrinkage_factor = 0.90 
            elif 100 < temp <= 110:
                st.session_state.resist_status = "Optimal"
                shrinkage_factor = 0.88 
                pr_color = '#FF0000' 
            elif 110 < temp < 140:
                st.session_state.resist_status = "Degraded"
                shrinkage_factor = 0.85 
                pr_color = '#8B4513' 
            elif temp >= 140:
                st.session_state.resist_status = "Charred"
                shrinkage_factor = 0.80 
                pr_color = '#2F4F4F' 

            baked_thickness = st.session_state.current_thickness * shrinkage_factor

            col1, col2, col3 = st.columns(3)
            col1.metric("Initial Thickness", f"{st.session_state.current_thickness:.3f} µm")
            col2.metric("Post-Bake Thickness", f"{baked_thickness:.3f} µm", delta=f"-{st.session_state.current_thickness - baked_thickness:.3f} µm")
            col3.metric("Resist Status", st.session_state.resist_status)

            st.markdown("---")
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.linspace(0, 10, 500)
            
            ax.fill_between(x, 0, -2, color='#A9A9A9', label='Silicon Substrate')
            ax.fill_between(x, 0, baked_thickness, color=pr_color, alpha=0.9, label=f'AZ 1505 ({st.session_state.resist_status})')
            
            ax.set_ylim(-2.5, 4.0) 
            ax.set_xlim(0, 10)
            ax.set_ylabel("Thickness (µm)")
            ax.set_xticks([])
            ax.legend(loc="upper right")
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)

    # --- Step 3 Logic ---
    elif step == "3. Maskless Exposure":
        st.header("Step 3: Direct Write Exposure (uMLA)")
        
        if st.session_state.resist_status in ["Degraded", "Charred", "Unbaked"]:
            st.error(f"Cannot expose wafer. The photoresist is currently {st.session_state.resist_status.lower()}.")
        else:
            st.markdown("Simulating the **uMLA maskless aligner** using a 365 nm UV light source.")
            st.sidebar.markdown("---")
            st.sidebar.subheader("uMLA Parameters")
            
            scan_mode = st.sidebar.radio("Scan Mode", ["Vector Scan", "Raster Scan"])
            pattern_type = st.sidebar.selectbox("Digital Write Pattern", ["Single Trench", "Double Trench", "Dense Grating"])
            dose = st.sidebar.slider("Exposure Dose (mJ/cm²)", min_value=20, max_value=200, value=90, step=10)
            defocus = st.sidebar.slider("Defocus (µm)", min_value=-20, max_value=20, value=0, step=5)
            
            if defocus == 0:
                st.success("✅ **Optimal focus:** Produces sharp, high-resolution features.")
            elif defocus > 0:
                st.info("ℹ️ **Positive defocus:** Beam focused above resist. Increases spot size, useful for larger features.")
            else:
                st.info("ℹ️ **Negative defocus:** Beam focused below resist. Can improve sidewall angles.")

            x = np.linspace(0, 10, 500) 
            base_profile = np.zeros_like(x)
            
            if pattern_type == "Single Trench":
                base_profile[(x > 4) & (x < 6)] = 1.0
            elif pattern_type == "Double Trench":
                base_profile[(x > 2) & (x < 4)] = 1.0
                base_profile[(x > 6) & (x < 8)] = 1.0
            elif pattern_type == "Dense Grating":
                for i in np.arange(1, 10, 1.5):
                    base_profile[(x > i) & (x < i + 0.6)] = 1.0

# --------- SCAN MODE DIFFERENCE ---------
if scan_mode == "Vector Scan":
    # Sharp pattern (direct writing)
    exposure_profile = base_profile.copy()

elif scan_mode == "Raster Scan":
    # Line-by-line scanning effect
    raster_profile = np.zeros_like(x)
    scan_lines = 40

    for i in range(scan_lines):
        shift = int(i * len(x) / scan_lines)
        shifted = np.roll(base_profile, shift)

        # simulate overlap (blur)
        blur = np.convolve(shifted, np.ones(8)/8, mode='same')
        raster_profile += blur

    # normalize
    exposure_profile = raster_profile / np.max(raster_profile)

    # add slight background exposure
    exposure_profile += 0.1
    exposure_profile = np.clip(exposure_profile, 0, 1)

# --------- DEFOCUS EFFECT ---------
blur_amount = abs(defocus)
if blur_amount > 0:
    window_size = int(blur_amount * 2.5)
    if window_size > 0:
        window = np.ones(window_size) / window_size
        exposure_profile = np.convolve(exposure_profile, window, mode='same')

st.session_state.received_dose = exposure_profile * dose
            
col1, col2, col3 = st.columns(3)
col1.metric("Operating Mode", scan_mode)
col2.metric("Laser Dose", f"{dose} mJ/cm²")
col3.metric("Defocus Offset", f"{defocus} µm")

st.markdown("---")
fig, ax = plt.subplots(figsize=(10, 4))
baked_thickness = st.session_state.current_thickness * 0.90 
            
ax.fill_between(x, 0, -2, color='#A9A9A9', label='Silicon Substrate')
ax.fill_between(x, 0, baked_thickness, color='#FF0000', alpha=0.8, label='Unexposed AZ 1505')
            
exposed_thickness = np.where(exposure_profile > 0.05, baked_thickness, 0)
ax.fill_between(x, 0, exposed_thickness, color='#FFFF00', alpha=np.clip(exposure_profile, 0, 1), label='Reacted AZ 1505')
            
ax.plot(x, exposure_profile * (baked_thickness + 1.0), color='blue', linestyle='-', linewidth=2, label='365nm Laser Profile')
            
ax.set_ylim(-2.5, 5.0) 
ax.set_xlim(0, 10)
ax.set_ylabel("Thickness / Intensity")
ax.set_xticks([])
ax.legend(loc="upper right", fontsize='small')
ax.grid(True, axis='y', linestyle='--', alpha=0.5)
     
if scan_mode == "Vector Scan":
        ax.set_title("Vector Scan: Sharp Pattern")
else:
        ax.set_title("Raster Scan: Blurred + Overlapping Pattern")

st.pyplot(fig)

    # --- Step 4 Logic ---
elif step == "4. Development":
        st.header("Step 4: Photoresist Development")
        
        if 'received_dose' not in st.session_state or np.max(st.session_state.received_dose) == 0:
             st.warning("⚠️ Please execute Step 3 (Maskless Exposure) first!")
        else:
            st.markdown("Simulating chemical development. Since AZ 1505 is a positive resist, exposed areas dissolve.")
            st.sidebar.markdown("---")
            st.sidebar.subheader("Development Parameters")
            
            dev_time = st.sidebar.slider("Development Time (seconds)", min_value=30, max_value=240, value=120, step=10)
            
            if dev_time < 90:
                st.info("ℹ️ **Under-developed:** Some reacted photoresist remains in the trenches.")
                clearance = dev_time / 120.0
            elif 90 <= dev_time <= 150:
                st.success("✅ **Optimal Development:** Exposed resist is fully dissolved.")
                clearance = 1.0
            else:
                st.warning("⚠️ **Over-developed:** Unexposed resist is starting to erode (dark erosion).")
                clearance = 1.0 + ((dev_time - 150) / 200.0)

            col1, col2 = st.columns(2)
            col1.metric("Developer Time", f"{dev_time} sec")
            col2.metric("Rinse Method", "DI Water")

            st.markdown("---")
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.linspace(0, 10, 500)
            baked_thickness = st.session_state.current_thickness * 0.90 
            
            ax.fill_between(x, 0, -2, color='#A9A9A9', label='Silicon Substrate')
            
            exposure_threshold = 20.0 
            final_profile = np.ones_like(x) * baked_thickness
            
            if clearance <= 1.0:
                dissolved_amount = np.where(st.session_state.received_dose > exposure_threshold, baked_thickness * clearance, 0)
                final_profile -= dissolved_amount
            else:
                dissolved_amount = np.where(st.session_state.received_dose > exposure_threshold, baked_thickness, 0)
                final_profile -= dissolved_amount
                final_profile -= (baked_thickness * (clearance - 1.0))
                
            final_profile = np.clip(final_profile, 0, baked_thickness)
            st.session_state.developed_profile = final_profile 
            
            ax.fill_between(x, 0, final_profile, color='#FF0000', alpha=0.8, label='Patterned AZ 1505')
            
            ax.set_ylim(-2.5, 4.0) 
            ax.set_xlim(0, 10)
            ax.set_ylabel("Thickness (µm)")
            ax.set_xticks([])
            ax.legend(loc="upper right")
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)

    # --- Step 5 Logic ---
    elif step == "5. Post-Bake (Hardbake)":
        st.header("Step 5: Post-Bake (Hardbake)")
        
        if 'developed_profile' not in st.session_state:
            st.warning("⚠️ Please execute Step 4 (Development) first!")
        else:
            st.markdown("Hardening the photoresist for the next process (e.g., etching or ion implantation).")
            st.sidebar.markdown("---")
            st.sidebar.subheader("Hardbake Parameters")
            
            hb_temp = st.sidebar.slider("Temperature (°C)", min_value=90, max_value=150, value=110, step=5)
            hb_time = st.sidebar.slider("Time (minutes)", min_value=1, max_value=10, value=5, step=1)
            
            if hb_temp < 100:
                st.info("ℹ️ **Low Temperature:** May not fully harden the resist.")
            elif 100 <= hb_temp <= 115:
                st.success("✅ **Optimal Hardbake:** Resist is hardened with minimal thermal distortion.")
            else:
                st.error("🚨 **Thermal Distortion (Reflow):** Temperature is too high. The photoresist is melting!")

            col1, col2 = st.columns(2)
            col1.metric("Hardbake Temp", f"{hb_temp} °C")
            col2.metric("Hardbake Time", f"{hb_time} min")

            st.markdown("---")
            fig, ax = plt.subplots(figsize=(10, 4))
            x = np.linspace(0, 10, 500)
            
            ax.fill_between(x, 0, -2, color='#A9A9A9', label='Silicon Substrate')
            profile = st.session_state.developed_profile.copy()
            
            if hb_temp > 115:
                reflow_amount = int((hb_temp - 115) * 1.5)
                if reflow_amount > 0:
                    window = np.ones(reflow_amount) / reflow_amount
                    profile = np.convolve(profile, window, mode='same')
                color = '#8B0000' 
            else:
                color = '#B22222' 
                
            ax.fill_between(x, 0, profile, color=color, alpha=0.9, label='Hardened AZ 1505 Pattern')
            
            ax.set_ylim(-2.5, 4.0) 
            ax.set_xlim(0, 10)
            ax.set_ylabel("Thickness (µm)")
            ax.set_xticks([])
            ax.legend(loc="upper right")
            ax.grid(True, axis='y', linestyle='--', alpha=0.5)
            st.pyplot(fig)

# --- TAB 5: QUIZ ---
with tab_quiz:
    st.header("Test Your Knowledge")
    st.markdown("1. Why does the final resist thickness decrease as spin speed increases?")
    st.markdown("2. In maskless lithography, what is the physical consequence of applying a positive defocus to the laser beam?")
    st.markdown("3. If you leave a wafer coated with positive photoresist in the developer for 4 minutes instead of 2 minutes, what defect will occur?")
    st.markdown("4. Why is the hardbake temperature generally higher than the softbake temperature?")
