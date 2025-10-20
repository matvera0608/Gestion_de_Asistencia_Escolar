def ejecutar_acción_presionando_Enter(botones, acciones, event):
  for clv, btn in botones.items():
    if event.widget == btn:
      print(f"Ejecutando acción: {clv}")
      acciones[clv]()
      return "break"
  
def mover_con_flechas(Treeview,caja_activa, botones_funcionales, cajasDeTexto, acciones, event=None):
  
  widget = event.widget
  tecla = event.keysym
  
  desde_lista_izquierda_hacia_caja = widget == Treeview and tecla == "Left"
  desde_lista_derecha_hacia_caja = widget == Treeview and tecla == "Right"
  
  tecla_hacia_arriba = tecla == "Up"
  tecla_hacia_abajo = tecla == "Down"
  tecla_hacia_derecha = tecla == "Right"
  tecla_hacia_izquierda = tecla == "Left"
  
  en_la_lista = widget == Treeview
  en_las_cajasDeTexto = widget in cajasDeTexto
  en_los_botonesCRUD = widget in botones_funcionales
  
  # Si el foco está en la ListBox, navegamos sus elementos. Pero esta sección es sólo para mover los registros
  if en_la_lista:
    if tecla_hacia_arriba and Treeview.curselection():
      índice_seleccionado = Treeview.curselection()[0]
      if índice_seleccionado > 0:
        Treeview.selection_clear(índice_seleccionado)
        Treeview.selection_set(índice_seleccionado - 1)
        Treeview.activate(índice_seleccionado - 1)
        acciones["Mostrar"]
        return "break"
    elif tecla_hacia_abajo and Treeview.curselection():
      índice_seleccionado = Treeview.curselection()[0]
      if índice_seleccionado < Treeview.size() - 1:
        Treeview.selection_clear(índice_seleccionado)
        Treeview.selection_set(índice_seleccionado + 1)
        Treeview.activate(índice_seleccionado + 1)
        acciones["Mostrar"]
        return "break"

   
    if (desde_lista_izquierda_hacia_caja or desde_lista_derecha_hacia_caja or tecla_hacia_izquierda or tecla_hacia_derecha):
      cajasDeTexto[0].focus_set
      return "break"
    
    
  elif en_los_botonesCRUD:
    índice_actual = botones_funcionales.index(widget)
    if tecla_hacia_arriba:
      botones_funcionales[índice_actual - 1].focus_set()
      return "break"
    elif tecla_hacia_abajo:
      botones_funcionales[índice_actual + 1].focus_set()
      return "break"
  
  elif en_las_cajasDeTexto:
    if not caja_activa:
      caja_activa.extend(cajasDeTexto)
        
    if widget not in caja_activa:
      print("Widget no está en caja activa")
      return "break"
    
    índice_actual = caja_activa.index(widget)

    if tecla_hacia_arriba:
      nuevo_índice =  (índice_actual - 1) % len(caja_activa)
      caja_activa[nuevo_índice].focus_set()
      return "break"

    elif tecla_hacia_abajo:
      nuevo_índice =  (índice_actual + 1) % len(caja_activa)
      caja_activa[nuevo_índice].focus_set()
      return "break"