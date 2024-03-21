


print("Cual es tu edad?")
edad = input()
nombres_por_edad = {
    "7": ["Alba"],
    "8": ["Alejandro"],
    "4": ["Javier"],
    "46": ["Jaime"],
    "43": ["Monica"],
    "82": ["Abuelita Juani", "Abuelito Sebas"],
    "1000": ["Rey Felipe VI", "Reina Letizia"],
}  
nombres = nombres_por_edad.get(edad, ["Desconocido"])
print(f"Como tu edad es {edad}, tu nombre puede ser: {', '.join(nombres)}")
