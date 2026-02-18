# rules.py - El Cerebro de Seguridad de Quantum AI

SEGURIDAD_SUPLEMENTOS = {
    "magnesio": {
        "pregunta": "¿Padeces de alguna condición renal o tomas fármacos para la hipertensión?",
        "alerta_si": "Insuficiencia renal, Bloqueo cardíaco, Toma de Diuréticos",
        "especialidad": "Nefrología / Cardiología"
    },
    "zinc": {
        "pregunta": "¿Consumes actualmente otros multivitamínicos o tienes anemia?",
        "alerta_si": "Uso prolongado sin cobre, Anemia sideroblástica",
        "especialidad": "Hematología / Nutrición Clínica"
    },
    "vitamina c": {
        "pregunta": "¿Tienes antecedentes de cálculos renales (piedras) o hemocromatosis?",
        "alerta_si": "Litiasis renal recurrente, Exceso de hierro",
        "especialidad": "Urología / Nutrición"
    },
    "complejo b": {
        "pregunta": "¿Padeces de ansiedad intensa o tienes programada alguna cirugía pronto?",
        "alerta_si": "Sobreestimulación nerviosa, Uso de metformina sin control",
        "especialidad": "Neurología / Medicina Interna"
    },
    "acido hialuronico": {
        "pregunta": "¿Tienes historial de enfermedades autoinmunes o inflamación articular aguda?",
        "alerta_si": "Brotes reumáticos activos",
        "especialidad": "Reumatología"
    }
}
