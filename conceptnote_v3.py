import streamlit as st
import PyPDF2
import re
import pandas as pd
import altair as alt
from typing import List, Dict, Tuple
 

# --- Initial Keyword Matrix (Hardcoded from Concept Note) ---
initial_indicator_keywords = {
    "Building Energy Efficiency": ["HVAC efficiency", "U-value", "building envelope", "energy demand", "energy performance", "energy simulation", "natural ventilation", "passive solar", "thermal insulation"],
    "Energy Consumption": ["energy-efficient equipment", "fuel-efficient vehicles", "energy optimization", "low-energy site operations", "reduced generator use", "hybrid construction machinery", "site energy plan"],
    "Thermal Performance": ["thermal envelope", "insulation", "U-value", "heat loss"],
    "Fuel Type for Equipment": ["Biodiesel", "alternative fuel", "low sulfur diesel", "renewable diesel", "clean fuel specification", "fuel switching", "emissions-compliant equipment", "non-fossil fuel use", "fuel quality standards"],
    "Lifecycle Carbon Reporting": ["EPD", "ISO 14040", "LCA", "carbon disclosure", "cradle to grave", "life cycle assessment", "embodied carbon",  "global warming potential", "whole life carbon", "whole of life emissions"],
    "Low Emission Construction Materials": ["EPD certified", "climate-friendly materials", "green concrete", "green steel", "low GWP products", "low embodied carbon", "low emission materials", "low-carbon concrete", "recycled content", "recycled steel", "sustainable aggregates"],
    "Renewable Energy Systems": ["solar PV", "solar thermal", "on-site renewables", "wind turbine", "clean energy supply"],
    "Renewable Energy Use": ["solar PV", "wind turbine", "renewable sources", "clean energy"],
    "Scope 1 GHG Emissions": ["low-emission equipment", "electric construction machinery", "no-idling policy", "diesel alternatives"],
    "Scope 2 GHG Emissions": ["renewable electricity", "grid decarbonization", "clean energy supplier", "green power purchase"],
    "Waste Management in Construction": ["construction waste plan", "waste diversion", "recycling targets", "deconstruction waste", "waste audit", "material reuse"],
    "Ecological Impacts": ["biodiversity management plan", "ecological preservation", "flora and fauna protection", "habitat conservation", "ecological corridors", "species impact assessment", "no net loss of biodiversity", "critical habitat avoidance"],
    "Land Use Change": ["controlled site clearance", "habitat protection", "reduced land disturbance", "preservation of existing vegetation", "grading minimization", "sensitive site planning", "ecological buffer zones"],
    "Sustainable Maintenance Planning": ["maintenance plan", "O&M manual", "sustainable operations", "long-term performance", "building tuning"],
    "Air Quality (PM)": ["dust suppression", "PM10 control", "particulate mitigation", "air quality management plan", "water spraying", "dust barriers", "low-dust equipment", "site air monitoring", "fine particle control"],
    "Biological Oxygen Demand (BOD)": ["biological oxygen demand", "BOD limits", "wastewater treatment", "treated discharge", "water effluent quality", "oxygen-demanding substances", "construction wastewater control", "water discharge permit", "EIA water standards"],
    "Chemical Oxygen Demand (COD)": ["chemical oxygen demand", "COD threshold", "treated effluent", "wastewater treatment", "organic load reduction", "water discharge monitoring", "pollutant load control", "construction site effluent standards", "COD testing protocol"],
    "Light Pollution": ["glare control", "shielded lighting", "cut-off luminaires", "dark-sky compliant", "timers or sensors", "reduced spill lighting", "low-impact exterior lighting", "night sky protection"],
    "Noise Pollution": ["noise monitoring", "noise control plan", "sound barriers", "decibel limits", "acoustic insulation", "quiet equipment", "low-noise machinery"],
    "Soil Contamination": ["soil remediation", "contamination prevention", "heavy metals testing", "hazardous waste containment", "soil quality monitoring", "clean soil management", "protective earthworks", "baseline soil assessment", "EIA soil standards"],
    "Suspended Solids": ["suspended solids control", "TSS limits", "sediment traps", "water filtration", "silt fencing", "particle settling tank", "turbidity control", "sedimentation basin", "construction runoff management"],
    "pH Level": ["pH monitoring", "acidity control", "alkalinity limits", "pH adjustment", "neutralization basin", "discharge pH standards", "pH compliant effluent", "pH testing protocol", "pH range compliance"],
    "Stormwater Management": ["stormwater", "runoff", "green infrastructure", "rainwater capture", "stormwater runoff", "permeable pavement", "rain garden", "swale", "detention basin"],
    "Water Harvesting and Efficiency": ["greywater system", "rainwater harvesting", "water recycling", "low-flow fixtures", "potable water reduction"],
    "Indoor Environmental Quality": ["IEQ", "acoustic comfort", "air changes per hour", "comfort metrics", "daylight factor", "daylighting", "indoor air quality", "low VOC", "thermal comfort", "ventilation rates"],
    "Stakeholder Transparency": ["stakeholder communication", "project transparency", "public disclosure", "open reporting", "stakeholder engagement strategy", "information sharing with communities", "project updates to stakeholders", "public access to project data", "transparency commitment clause"],
    "Training and Capacity Building": ["construction workforce training", "capacity building plan", "upskilling program", "technical training for laborers", "site-based skills development", "vocational training", "certified training requirement", "on-the-job training", "education for site workers"],
    "Community Co-Design": ["community engagement", "participatory planning", "stakeholder consultation", "co-design process", "local stakeholder input", "community design workshops", "inclusive planning sessions", "collaborative design", "engagement with affected communities"],
    "Community Engagement": ["co-design", "community feedback", "community input", "feedback sessions", "participatory planning", "public consultation", "public meetings", "stakeholder consultation", "stakeholder input"],
    "Local Employment": ["community employment", "regional workforce", "local hiring", "community-based labor", "regional workforce participation", "employment of local residents", "priority to local workers", "community employment target", "inclusion of local subcontractors", "local job creation"],
    "Gender Inclusion": ["women participation", "female workforce", "gender equity", "women in construction", "female labor participation", "gender-inclusive hiring", "women employment target", "gender-responsive workforce plan", "gender balance in project teams", "inclusion of women-owned subcontractors", "gender diversity reporting"],
    "Gender Responsive Design": ["gender-inclusive design", "safe design for women", "gender-sensitive infrastructure", "female-friendly facilities", "women’s access and safety", "gender-informed site layout", "inclusive public space", "stakeholder feedback on gender needs", "universal design for gender inclusion"],
    "Inclusive Design & Accessibility": ["universal design", "accessible building", "disability access", "barrier-free", "inclusive space"],
    "Worker Health & Safety": ["occupational health and safety", "HSE plan", "personal protective equipment", "PPE compliance", "site safety management", "injury prevention", "safety training", "hazard control", "safety monitoring protocol", "zero accident policy"],
    "Health & Well-being": ["indoor air quality", "daylighting", "low VOC", "thermal comfort", "acoustic comfort", "ventilation rates"],
    "Environmental Cost Internalization": ["restoration costs", "ecological rehabilitation", "green recovery"],
    "Social Cost Internalization": ["resettlement costs", "displacement compensation"],
    "Building Information Modelling (BIM) Use": ["BIM", "BIM brief", "BIM coordination", "BIM execution plan", "building information modelling"],
    "Local Content and Sourcing": ["local procurement", "economic uplift", "regional impact", "local content requirement", "regionally sourced materials", "local suppliers", "community-based sourcing", "preference for local vendors", "domestic procurement target", "locally manufactured inputs", "use of local subcontractors"],
    "Local Economic Benefits": ["local economic development", "support for community enterprises", "local job creation", "inclusive procurement", "regional economic impact", "engagement of local businesses", "SME participation", "community-based suppliers", "local value retention"],
    "Circular Construction Practices": ["design for disassembly", "modular construction", "component reuse", "material passport", "circular design"],
    "Structure Durability": ["design life", "structural longevity", "durable infrastructure", "resilience to degradation", "maintenance-free period", "long-life materials", "infrastructure lifespan", "extended service life", "low-maintenance design"],
    "Lifecycle Cost Analysis": ["lifecycle cost analysis", "LCCA", "whole life costing", "long-term cost evaluation", "cost-benefit analysis", "maintenance cost forecasting", "total cost of ownership", "value for money over lifecycle"]
  }
 

# --- Streamlit App ---
def main():
    st.title("Sustainability Assessment Tool")
 

    uploaded_files = st.file_uploader("Upload PDF documents/contracts", type="pdf", accept_multiple_files=True)
 

    # --- Keyword Management Interface ---
    st.sidebar.header("Manage Keywords")
    keyword_data = display_keyword_management()
 

    all_analysis_results = []
    if uploaded_files:
        for uploaded_file in uploaded_files:
            text, pages, filename = extract_text_and_page_info_from_pdf(uploaded_file)
            if text:
                analysis_results = analyze_document(text, pages, filename, keyword_data)
                all_analysis_results.append(analysis_results)
            else:
                st.error(f"Could not extract text from {uploaded_file.name}. Please ensure it's a readable PDF.")
 

        if all_analysis_results:
            display_overall_results(all_analysis_results)
            display_detailed_results(all_analysis_results)
 

def extract_text_and_page_info_from_pdf(uploaded_file) -> Tuple[str, List[Dict], str]:
    try:
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        pages = []
        for i, page in enumerate(pdf_reader.pages):
            page_text = page.extract_text() or ""
            text += page_text + " "
            pages.append({"page": i + 1, "text": page_text})
        return text, pages, uploaded_file.name
    except Exception as e:
        st.error(f"Error extracting text from {uploaded_file.name}: {e}")
        return "", [], uploaded_file.name
 

def analyze_document(text: str, pages: List[Dict], filename: str, indicator_keywords: Dict[str, List[str]]) -> Dict:
    text = text.lower()
    detected_indicators = {}
    for indicator, keywords in indicator_keywords.items():
        for keyword in keywords:
            matches = list(re.finditer(r"\b" + re.escape(keyword) + r"\b", text))
            if matches:
                if indicator not in detected_indicators:
                    detected_indicators[indicator] = []
                detected_indicators[indicator].append({
                    "keyword": keyword,
                    "locations": get_keyword_locations(matches, pages),
                    "filename": filename
                })
 

    num_indicators = len(detected_indicators)
    dimension_coverage = get_dimension_coverage(detected_indicators)
    ambition_level = get_ambition_level(num_indicators, dimension_coverage)
 

    return {
        "num_indicators": num_indicators,
        "dimension_coverage": dimension_coverage,
        "matched_indicators": detected_indicators,
        "ambition_level": ambition_level,
        "extracted_from": filename
    }
 

def get_keyword_locations(matches: List[re.Match], pages: List[Dict]) -> List[str]:
    locations = []
    for match in matches:
        start = match.start()
        for page in pages:
            if start <= len(page["text"]):
                locations.append(f"Page {page['page']}, Char {start}")
                break
            else:
                start -= len(page["text"]) + 1
    return locations
 

def get_dimension_coverage(detected_indicators: Dict[str, List]) -> Dict[str, int]:
    environmental_indicators = ["Building Energy Efficiency", "Energy Consumption", "Thermal Performance", "Fuel Type for Equipment", "Lifecycle Carbon Reporting", "Low Emission Construction Materials", "Renewable Energy Systems", "Renewable Energy Use", "Scope 1 GHG Emissions", "Scope 2 GHG Emissions", "Waste Management in Construction", "Ecological Impacts", "Land Use Change", "Sustainable Maintenance Planning", "Air Quality (PM)", "Biological Oxygen Demand (BOD)", "Chemical Oxygen Demand (COD)", "Light Pollution", "Noise Pollution", "Soil Contamination", "Suspended Solids", "pH Level", "Stormwater Management", "Water Harvesting and Efficiency", "Indoor Environmental Quality"]
    social_indicators = ["Stakeholder Transparency", "Training and Capacity Building", "Community Co-Design", "Community Engagement", "Local Employment", "Gender Inclusion", "Gender Responsive Design", "Inclusive Design & Accessibility", "Worker Health & Safety", "Health & Well-being"]
    economic_indicators = ["Environmental Cost Internalization", "Social Cost Internalization", "Building Information Modelling (BIM) Use", "Local Content and Sourcing", "Local Economic Benefits", "Circular Construction Practices", "Structure Durability", "Lifecycle Cost Analysis"]
 

    environmental_count = len(set(environmental_indicators) & set(detected_indicators.keys()))
    social_count = len(set(social_indicators) & set(detected_indicators.keys()))
    economic_count = len(set(economic_indicators) & set(detected_indicators.keys()))
 

    return {
        "Environmental": environmental_count,
        "Social": social_count,
        "Economic": economic_count
    }
 

def get_ambition_level(num_indicators: int, dimension_coverage: Dict[str, int]) -> str:
    if 1 <= num_indicators <= 4:
        return "Low"
    elif 5 <= num_indicators <= 9 and sum(dimension_coverage.values()) >= 2:
        return "Medium"
    elif num_indicators >= 10 and all(count > 0 for count in dimension_coverage.values()):
        return "High"
    else:
        return "Low"
 

def display_overall_results(all_analysis_results: List[Dict]):
    st.header("Overall Analysis Summary")
 

    # --- Overall Ambition Level Pie Chart ---
    st.subheader("Overall Ambition Level")
    overall_ambition_data = pd.DataFrame({
        'Level': ['Low', 'Medium', 'High'],
        'Count': [sum(1 for res in all_analysis_results if res['ambition_level'] == 'Low'),
                  sum(1 for res in all_analysis_results if res['ambition_level'] == 'Medium'),
                  sum(1 for res in all_analysis_results if res['ambition_level'] == 'High')]
    })
    pie_chart = alt.Chart(overall_ambition_data).mark_arc().encode(
        theta='Count',
        color='Level',
        tooltip=['Level', 'Count']
    ).properties(title="Ambition Level Distribution")
    st.altair_chart(pie_chart, use_container_width=True)
 

    # --- Average Number of Indicators ---
    avg_indicators = sum(res['num_indicators'] for res in all_analysis_results) / len(all_analysis_results)
    st.subheader(f"Average Number of Indicators Detected: {avg_indicators:.2f}")
 

    # --- Overall Dimension Coverage ---
    st.subheader("Overall Dimension Coverage")
    overall_dimension_data = {
        'Environmental': sum(res['dimension_coverage']['Environmental'] for res in all_analysis_results),
        'Social': sum(res['dimension_coverage']['Social'] for res in all_analysis_results),
        'Economic': sum(res['dimension_coverage']['Economic'] for res in all_analysis_results)
    }
    dimension_df = pd.DataFrame(list(overall_dimension_data.items()), columns=['Dimension', 'Count'])
    chart = alt.Chart(dimension_df).mark_bar().encode(
        x=alt.X('Dimension', sort=None),
        y='Count',
        color=alt.Color('Dimension', legend=None),
        tooltip=['Dimension', 'Count']
    ).properties(title="Combined Dimension Coverage")
    st.altair_chart(chart, use_container_width=True)
 

def display_detailed_results(all_analysis_results: List[Dict]):
    st.header("Detailed Results per Document")
 

    for result in all_analysis_results:
        st.subheader(f"Analysis of: {result['extracted_from']}")
 

        # --- Ambition Level ---
        st.markdown(f"**Ambition Level:** <div style='font-size: 24px;'>{result['ambition_level']}</div>", unsafe_allow_html=True)
 

        # --- Number of Indicators ---
        st.markdown(f"**Number of Indicators Detected:** <div style='font-size: 24px;'>{result['num_indicators']}</div>", unsafe_allow_html=True)
 

        # --- Dimension Coverage Bar Chart ---
        st.subheader("Dimension Coverage")
        dimension_data = pd.DataFrame(list(result["dimension_coverage"].items()), columns=['Dimension', 'Count'])
        chart = alt.Chart(dimension_data).mark_bar().encode(
            x=alt.X('Dimension', sort=None),
            y='Count',
            color=alt.Color('Dimension', legend=None),
            tooltip=['Dimension', 'Count']
        ).properties(width=300, height=300)
        st.altair_chart(chart, use_container_width=True)
 

        # --- Matched Indicators and Keywords Table ---
        st.subheader("Matched Indicators and Keywords")
        if result["matched_indicators"]:
            data = []
            for indicator, matches in result["matched_indicators"].items():
                for match in matches:
                    locations = "<br>".join(match["locations"])
                    data.append({"Indicator": indicator, "Keyword": match["keyword"], "Locations": locations, "Document": result['extracted_from']}) # Include filename
            df = pd.DataFrame(data)
            st.table(df)
        else:
            st.write("No indicators matched in this document.")
 

def display_keyword_management():
    keyword_data = initial_indicator_keywords.copy()
    st.write("### Indicators and Keywords")
    for indicator, keywords in initial_indicator_keywords.items():
        expanded = st.checkbox(indicator, value=True, key=f"expand_{indicator}")
        if expanded:
            keyword_string = ", ".join(keywords)
            new_keywords = st.text_input(f"Keywords for {indicator}:", value=keyword_string, key=indicator)
            keyword_data[indicator] = [k.strip() for k in new_keywords.split(",")]
 

    new_indicator = st.text_input("New Indicator:", key="new_indicator")
    new_indicator_keywords = st.text_input(f"Keywords for {new_indicator}:", key="new_indicator_keywords")
    if new_indicator and new_indicator_keywords:
        keyword_data[new_indicator] = [k.strip() for k in new_indicator_keywords.split(",")]
 

    return keyword_data
 

if __name__ == "__main__":
    main()