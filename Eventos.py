from Elementos import colores

def mover_con_flechas(treeview, cajas, botones, acciones, event):
    widget = event.widget
    tecla = event.keysym
    
    cajas = [c for c in cajas if hasattr(c, "focus_set")]
    botones = [b for b in botones if hasattr(b, "focus_set")]
    
    ordenes_widget = list(cajas) + list(botones)
    
    
    if not ordenes_widget:
        return "break"
    
    try:
        índice_actual = ordenes_widget.index(widget)
    except:
        índice_actual = - 1
    #--- BOOLEANOS PARA LA NAVEGACIÓN ---#
    interacción_con_Treeview = widget == treeview
    interacción_con_Cajas = widget in cajas
    interacción_con_Botones = widget in botones
    
    arriba = tecla == "Up"
    abajo = tecla == "Down"
    izquierda = tecla == "Left"
    derecha = tecla == "Right"
    presionarEnter = tecla == "Return"
    
    
    if interacción_con_Treeview:
        if arriba and treeview.selection():
            iid = treeview.selection()[0]
            idx = treeview.index(iid)
            if idx > 0:
                newiid = treeview.get_children()[idx]
                treeview.selection_set(newiid)
                treeview.focus(newiid)
                treeview.see(newiid)
                acciones["Mostrar"]()
            return "break"
        elif abajo and treeview.selection():
            iid = treeview.selection()[0]
            idx = treeview.index(iid)
            if idx < len(treeview.get_children()) - 1:
                newiid = treeview.get_children()[idx]
                treeview.selection_set(newiid)
                treeview.focus(newiid)
                treeview.see(newiid)
                acciones["Mostrar"]()
            return "break"
          
        if izquierda and cajas:
            cajas[0].focus_set()
            return "break"
        
        elif derecha and botones:
            botones[0].focus_set()
            return "break"
    
    if interacción_con_Cajas:
        if arriba:
            nuevo_índice = (índice_actual - 1) % len(ordenes_widget)
            ordenes_widget[nuevo_índice].focus_set()
            return "break"
        elif abajo:
            nuevo_índice = (índice_actual + 1) % len(ordenes_widget)
            ordenes_widget[nuevo_índice].focus_set()
            return "break"
        
        elif izquierda and botones:
            botones[0].focus_set()
            return "break"
        
        elif derecha and treeview:
            treeview.focus_set()
            return "break"
        
    if interacción_con_Botones:
        if arriba:
            nuevo_idx = (índice_actual - 1) % len(ordenes_widget)
            ordenes_widget[nuevo_idx].focus_set()
            return "break"

        elif abajo:
            nuevo_idx = (índice_actual + 1) % len(ordenes_widget)
            ordenes_widget[nuevo_idx].focus_set()
            return "break"

        elif izquierda:
            if cajas:
                cajas[0].focus_set()
            return "break"

        elif derecha:
            if treeview:
                treeview.focus_set()
            return "break"

        elif presionarEnter:
            widget.invoke()
            return "break"
    
    return None