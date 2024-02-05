from .models import Reservation

def calendar_link_generator(reservation: Reservation):
    """Generates a link to add the event to the user's google calendar."""
    base_url = "https://calendar.google.com/calendar/r/eventedit"
    text = f"{reservation.ticket.event.title} - {reservation.ticket.event.date}".replace(" ", "+")
    # dates template: YYYYMMDDTHHmmSSZ/YYYYMMDDTHHmmSSZ
    dates = (
        f"{reservation.ticket.event.date.strftime('%Y%m%d')}T"
        f"{reservation.ticket.event.date.strftime('%H%M%S')}Z/"
        f"{reservation.ticket.event.end_date.strftime('%Y%m%d')}T"
        f"{reservation.ticket.event.end_date.strftime('%H%M%S')}Z"
    )
    details = f"{reservation.ticket.event.description}".replace(" ", "+")
    sprop = "name:Evently"
    
    location = None
    if reservation.ticket.event.location not in [None, ""]:
        location = f"{reservation.ticket.event.location.address}".replace(" ", "+")
    
    final_url = f"{base_url}?text={text}&dates={dates}&details={details}&sprop={sprop}"
    if location:
        final_url += f"&location={location}"
    
    return final_url