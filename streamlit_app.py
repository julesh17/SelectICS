import streamlit as st
from icalendar import Calendar
from datetime import datetime, date
import io
import os

st.title("Filtrage d'événements ICS")

uploaded_file = st.file_uploader("Importer un fichier .ics", type=["ics"])

if uploaded_file is not None:
    # Lecture du contenu du fichier
    cal = Calendar.from_ical(uploaded_file.read())

    # Récupération des bornes min et max pour aider l’utilisateur
    dates = []
    for component in cal.walk("VEVENT"):
        if component.get("dtstart"):
            dt = component.decoded("dtstart")
            if isinstance(dt, datetime):
                dt = dt.date()
            dates.append(dt)

    if dates:
        min_date, max_date = min(dates), max(dates)
        st.write(f"Événements disponibles entre **{min_date}** et **{max_date}**")

        # Sélecteurs de dates
        start_date = st.date_input("Date de début", min_date, min_value=min_date, max_value=max_date)
        end_date = st.date_input("Date de fin", max_date, min_value=min_date, max_value=max_date)

        if start_date > end_date:
            st.warning("⚠️ La date de début est postérieure à la date de fin. Veuillez corriger votre sélection.")
        else:
            if st.button("Générer le nouveau fichier .ics"):
                # Nouveau calendrier
                new_cal = Calendar()
                for key, value in cal.items():
                    new_cal.add(key, value)

                # Filtrer les événements
                for component in cal.walk("VEVENT"):
                    dtstart = component.decoded("dtstart")
                    if isinstance(dtstart, datetime):
                        dt_event = dtstart.date()
                    else:
                        dt_event = dtstart

                    if start_date <= dt_event <= end_date:
                        new_cal.add_component(component)

                # Construction du nom du fichier
                base_name, _ = os.path.splitext(uploaded_file.name)
                start_str = start_date.strftime("%d_%m_%Y")
                end_str = end_date.strftime("%d_%m_%Y")
                new_filename = f"{base_name}_du_{start_str}_au_{end_str}.ics"

                # Écriture dans un buffer
                output = io.BytesIO(new_cal.to_ical())
                st.download_button(
                    label="📥 Télécharger le fichier filtré",
                    data=output,
                    file_name=new_filename,
                    mime="text/calendar"
                )
