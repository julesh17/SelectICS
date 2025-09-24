import streamlit as st
from icalendar import Calendar, Event
from datetime import datetime, date
import pytz
import io

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
            st.error("La date de début doit être avant la date de fin.")
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

                # Écriture dans un buffer
                output = io.BytesIO(new_cal.to_ical())
                st.download_button(
                    label="Télécharger le fichier filtré",
                    data=output,
                    file_name="filtre.ics",
                    mime="text/calendar"
                )
