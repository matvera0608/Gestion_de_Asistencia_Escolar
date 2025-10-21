def mover_con_flechas(treeview, cajas, botones, acciones, event):
    widget = event.widget
    tecla = event.keysym
    
    cajas = [c for c in cajas if hasattr(c, "focus_set")]
    botones = [b for b in botones if hasattr(b, "focus_set")]
   
   

    return None