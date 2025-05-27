def publicar_tickets_en_jira(analisis: dict):
    resultados = []
    tickets = analisis.get("tickets", [])

    for ticket in tickets:
        summary = ticket.get("summary")
        tipo = ticket.get("tipo", "Story")
        criterios = ticket.get("criterios_de_aceptacion", [])
        descripcion = ticket.get("description", "")

        # Formatear descripción final con criterios de aceptación
        criterios_md = "\n\n**Criterios de aceptación:**\n" + "\n".join(f"- {c}" for c in criterios) if criterios else ""
        descripcion_final = descripcion.strip() + criterios_md

        status, res = crear_issue(summary=summary, description=descripcion_final, issue_type=tipo)
        resultados.append({
            "status": status,
            "issue": res
        })
    return resultados