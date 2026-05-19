const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  AlignmentType, HeadingLevel, BorderStyle, WidthType, ShadingType,
  LevelFormat, PageNumber, Header, Footer
} = require('docx');
const fs = require('fs');

const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
const borders = { top: border, bottom: border, left: border, right: border };

const warningBorder = { style: BorderStyle.SINGLE, size: 2, color: "E8A000" };
const warningBorders = { top: warningBorder, bottom: warningBorder, left: warningBorder, right: warningBorder };

function heading1(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_1,
    children: [new TextRun({ text, bold: true, size: 32, font: "Arial" })],
    spacing: { before: 360, after: 180 },
  });
}

function heading2(text) {
  return new Paragraph({
    heading: HeadingLevel.HEADING_2,
    children: [new TextRun({ text, bold: true, size: 26, font: "Arial", color: "2E75B6" })],
    spacing: { before: 240, after: 120 },
  });
}

function normal(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Arial", size: 22, ...opts })],
    spacing: { before: 60, after: 60 },
  });
}

function bullet(text, bold = false) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ text, font: "Arial", size: 22, bold })],
    spacing: { before: 40, after: 40 },
  });
}

function code(text) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Courier New", size: 20, color: "1F3864" })],
    spacing: { before: 40, after: 40 },
    indent: { left: 720 },
    shading: { fill: "EEF2F7", type: ShadingType.CLEAR },
  });
}

function warningBox(text) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders: warningBorders,
            width: { size: 9360, type: WidthType.DXA },
            shading: { fill: "FFF8E6", type: ShadingType.CLEAR },
            margins: { top: 120, bottom: 120, left: 180, right: 180 },
            children: [new Paragraph({
              children: [
                new TextRun({ text: "⚠ IMPORTANTE: ", font: "Arial", size: 22, bold: true, color: "E8A000" }),
                new TextRun({ text, font: "Arial", size: 22 }),
              ],
              spacing: { before: 0, after: 0 },
            })],
          })
        ]
      })
    ]
  });
}

function infoBox(text) {
  return new Table({
    width: { size: 9360, type: WidthType.DXA },
    columnWidths: [9360],
    rows: [
      new TableRow({
        children: [
          new TableCell({
            borders,
            width: { size: 9360, type: WidthType.DXA },
            shading: { fill: "E8F4FD", type: ShadingType.CLEAR },
            margins: { top: 120, bottom: 120, left: 180, right: 180 },
            children: [new Paragraph({
              children: [
                new TextRun({ text: "ℹ ", font: "Arial", size: 22, bold: true, color: "2E75B6" }),
                new TextRun({ text, font: "Arial", size: 22 }),
              ],
              spacing: { before: 0, after: 0 },
            })],
          })
        ]
      })
    ]
  });
}

function spacer() {
  return new Paragraph({ children: [new TextRun("")], spacing: { before: 80, after: 80 } });
}

function divider() {
  return new Paragraph({
    children: [new TextRun("")],
    border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 1 } },
    spacing: { before: 120, after: 120 },
  });
}

const doc = new Document({
  numbering: {
    config: [
      {
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
      {
        reference: "numbers",
        levels: [{
          level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      },
    ]
  },
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      {
        id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 32, bold: true, font: "Arial", color: "1F3864" },
        paragraph: { spacing: { before: 360, after: 180 }, outlineLevel: 0 }
      },
      {
        id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 26, bold: true, font: "Arial", color: "2E75B6" },
        paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1 }
      },
    ]
  },
  sections: [{
    properties: {
      page: {
        size: { width: 12240, height: 15840 },
        margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
      }
    },
    headers: {
      default: new Header({
        children: [new Paragraph({
          children: [new TextRun({ text: "Proyecto Helen — Guia de Configuracion del Foco RGB", font: "Arial", size: 18, color: "888888" })],
          alignment: AlignmentType.RIGHT,
          border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 1 } },
        })]
      })
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          children: [
            new TextRun({ text: "Pagina ", font: "Arial", size: 18, color: "888888" }),
            new TextRun({ children: [PageNumber.CURRENT], font: "Arial", size: 18, color: "888888" }),
            new TextRun({ text: " de ", font: "Arial", size: 18, color: "888888" }),
            new TextRun({ children: [PageNumber.TOTAL_PAGES], font: "Arial", size: 18, color: "888888" }),
          ],
          alignment: AlignmentType.CENTER,
          border: { top: { style: BorderStyle.SINGLE, size: 4, color: "CCCCCC", space: 1 } },
        })]
      })
    },
    children: [
      // PORTADA
      new Paragraph({
        children: [new TextRun({ text: "Proyecto Helen", font: "Arial", size: 52, bold: true, color: "1F3864" })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 480, after: 120 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Guia de Configuracion del Foco RGB RadioShack", font: "Arial", size: 30, color: "2E75B6" })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 120 },
      }),
      new Paragraph({
        children: [new TextRun({ text: "Control IoT via protocolo Tuya Local", font: "Arial", size: 24, color: "888888", italics: true })],
        alignment: AlignmentType.CENTER,
        spacing: { before: 0, after: 480 },
      }),
      divider(),
      spacer(),

      // REQUISITOS PREVIOS
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Requisitos Previos", font: "Arial", size: 32, bold: true })], spacing: { before: 360, after: 180 } }),
      normal("Antes de comenzar, asegurate de tener lo siguiente instalado en tu laptop:"),
      spacer(),
      bullet("Python (verificar con: py --version)"),
      bullet("Node.js (verificar con: npm --version)"),
      bullet("Git (verificar con: git --version)"),
      bullet("App SmartLife instalada en tu celular"),
      bullet("Foco RGB RadioShack fisicamente en tu poder"),
      spacer(),
      warningBox("El foco RGB solo funciona en redes WiFi de 2.4 GHz. Las redes de 5 GHz no son compatibles."),
      spacer(),
      divider(),

      // PASO 1
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Paso 1: Conectar el Foco a tu Red WiFi", font: "Arial", size: 32, bold: true })], spacing: { before: 360, after: 180 } }),
      normal("Sigue estos pasos en la aplicacion SmartLife de tu celular:"),
      spacer(),
      bullet('Abre SmartLife y toca el boton "+" (arriba a la derecha)'),
      bullet('Selecciona "Agregar dispositivo" o "Add Device"'),
      bullet('Busca la categoria "Lighting" o "Light" y selecciona el tipo de foco'),
      bullet("Selecciona tu red WiFi de casa (asegurate que sea 2.4 GHz)"),
      bullet("Ingresa la contrasena de tu red WiFi"),
      bullet("Espera a que se complete el emparejamiento (30-60 segundos)"),
      spacer(),
      infoBox("Si tu router tiene dos redes (2.4 GHz y 5 GHz), generalmente la red de 2.4 GHz tiene el nombre sin sufijo o con '_2.4G'. Conectate a esa."),
      spacer(),
      divider(),

      // PASO 2
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Paso 2: Obtener el IP Local del Foco", font: "Arial", size: 32, bold: true })], spacing: { before: 360, after: 180 } }),
      normal("El protocolo Tuya local requiere el IP local del foco en tu red, no el IP publico."),
      spacer(),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: "2.1 Verificar el MAC Address del foco", font: "Arial", size: 26, bold: true, color: "2E75B6" })], spacing: { before: 240, after: 120 } }),
      bullet("En SmartLife, toca el foco para abrirlo"),
      bullet("Toca el icono de engranaje (ajustes) arriba a la derecha"),
      bullet('Selecciona "Device Information" o "Informacion del dispositivo"'),
      bullet("Anota el MAC Address del foco:"),
      spacer(),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3000, 6360],
        rows: [
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3000, type: WidthType.DXA }, shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "MAC Address", font: "Arial", size: 22, bold: true })] })] }),
              new TableCell({ borders, width: { size: 6360, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "b8:06:0d:dd:ad:ce", font: "Courier New", size: 22, bold: true, color: "1F3864" })] })] }),
            ]
          }),
        ]
      }),
      spacer(),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: "2.2 Encontrar el IP Local desde el router/celular", font: "Arial", size: 26, bold: true, color: "2E75B6" })], spacing: { before: 240, after: 120 } }),
      bullet("En tu celular, ve a Ajustes > WiFi > toca tu red WiFi conectada"),
      bullet('Busca la opcion "Dispositivos conectados" o "Connected devices"'),
      bullet("Busca el dispositivo con el MAC Address b8:06:0d:dd:ad:ce"),
      bullet("Anota su IP (sera algo como 192.168.x.x o 10.x.x.x)"),
      spacer(),
      warningBox("El IP puede cambiar cada vez que el foco se reconecta. Si algo no funciona, repite este paso para obtener el IP actualizado."),
      spacer(),
      divider(),

      // PASO 3
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Paso 3: Obtener la Local Key", font: "Arial", size: 32, bold: true })], spacing: { before: 360, after: 180 } }),
      normal("La Local Key es necesaria para comunicarse con el foco. Se puede cambiar al reconectar el foco a una nueva red."),
      spacer(),
      bullet("Abre una terminal en tu laptop y corre:"),
      code("pip install tinytuya"),
      spacer(),
      bullet("Luego corre el wizard:"),
      code("py -m tinytuya wizard"),
      spacer(),
      bullet("Ingresa los siguientes datos cuando te los pida:"),
      spacer(),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3500, 5860],
        rows: [
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Campo", font: "Arial", size: 22, bold: true })] })] }),
              new TableCell({ borders, width: { size: 5860, type: WidthType.DXA }, shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Valor", font: "Arial", size: 22, bold: true })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "API Key", font: "Arial", size: 22 })] })] }),
              new TableCell({ borders, width: { size: 5860, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "7vrqh5gq3sm95extwsgj", font: "Courier New", size: 20, color: "1F3864" })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "API Secret", font: "Arial", size: 22 })] })] }),
              new TableCell({ borders, width: { size: 5860, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "a27dcb22b5564310ac1b7b4b717f04fd", font: "Courier New", size: 20, color: "1F3864" })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Device ID (opcional)", font: "Arial", size: 22 })] })] }),
              new TableCell({ borders, width: { size: 5860, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "ebe997370c6c715b97qsgw", font: "Courier New", size: 20, color: "1F3864" })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Region", font: "Arial", size: 22 })] })] }),
              new TableCell({ borders, width: { size: 5860, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "us", font: "Courier New", size: 20, color: "1F3864" })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Poll local devices?", font: "Arial", size: 22 })] })] }),
              new TableCell({ borders, width: { size: 5860, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "y", font: "Courier New", size: 20, color: "1F3864" })] })] }),
            ]
          }),
        ]
      }),
      spacer(),
      bullet('Cuando termine, se generara un archivo "devices.json" en la carpeta actual'),
      bullet('Abrelo y copia el valor del campo "key" — esa es tu nueva Local Key'),
      spacer(),
      divider(),

      // PASO 4
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Paso 4: Configurar el archivo .env", font: "Arial", size: 32, bold: true })], spacing: { before: 360, after: 180 } }),
      bullet("Clona el repositorio en tu laptop:"),
      code("git clone -b Sashil-RS https://github.com/Mrc002/Uabc_Helen_2026_1.git"),
      spacer(),
      bullet("Entra a la carpeta del backend:"),
      code("cd Uabc_Helen_2026_1/Helen-Web/backend/websocket-server"),
      spacer(),
      bullet("Copia el archivo de ejemplo:"),
      code("copy .env.example .env"),
      spacer(),
      bullet("Abre el archivo .env y actualiza estos dos valores:"),
      spacer(),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [3500, 5860],
        rows: [
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Variable", font: "Arial", size: 22, bold: true })] })] }),
              new TableCell({ borders, width: { size: 5860, type: WidthType.DXA }, shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Valor a poner", font: "Arial", size: 22, bold: true })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "TUYA_IP", font: "Courier New", size: 22, color: "1F3864" })] })] }),
              new TableCell({ borders, width: { size: 5860, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "IP local obtenido en Paso 2 (ej: 192.168.1.50)", font: "Arial", size: 22 })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 3500, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "TUYA_LOCAL_KEY", font: "Courier New", size: 22, color: "1F3864" })] })] }),
              new TableCell({ borders, width: { size: 5860, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Key obtenida del devices.json en Paso 3", font: "Arial", size: 22 })] })] }),
            ]
          }),
        ]
      }),
      spacer(),
      divider(),

      // PASO 5
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Paso 5: Instalar Dependencias y Correr", font: "Arial", size: 32, bold: true })], spacing: { before: 360, after: 180 } }),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: "Terminal 1 — Backend", font: "Arial", size: 26, bold: true, color: "2E75B6" })], spacing: { before: 240, after: 120 } }),
      code("cd Helen-Web/backend/websocket-server"),
      code("pip install -r requirements.txt"),
      code("py server.py"),
      spacer(),
      infoBox('El servidor esta listo cuando ves: "Running on http://0.0.0.0:5001"'),
      spacer(),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: "Terminal 2 — Frontend", font: "Arial", size: 26, bold: true, color: "2E75B6" })], spacing: { before: 240, after: 120 } }),
      code("cd Helen-Web/frontend/web-app"),
      code("npm install"),
      code("npm run dev"),
      spacer(),
      bullet("Abre tu navegador en: http://localhost:3000"),
      spacer(),
      divider(),

      // PASO 6
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Paso 6: Verificar que Funciona", font: "Arial", size: 32, bold: true })], spacing: { before: 360, after: 180 } }),
      bullet('Ve a la pantalla "Mis Dispositivos" en la aplicacion Helen'),
      bullet('El indicador del Foco RGB debe mostrar "ENCENDIDO" o "APAGADO"'),
      spacer(),
      warningBox('Si dice "SIN CONEXION": verifica que el IP en tu .env sea correcto y que la laptop este en la misma red WiFi que el foco.'),
      spacer(),
      divider(),

      // COMANDOS
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Comandos para Controlar el Foco", font: "Arial", size: 32, bold: true })], spacing: { before: 360, after: 180 } }),
      normal("Con el backend corriendo, abre una tercera terminal en Helen-Web/backend/websocket-server y sustituye TU_IP y TU_KEY con tus valores:"),
      spacer(),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: "Encender el foco:", font: "Arial", size: 26, bold: true, color: "2E75B6" })], spacing: { before: 240, after: 120 } }),
      code('py -c "import tinytuya; d = tinytuya.BulbDevice(\'ebe997370c6c715b97qsgw\', \'TU_IP\', \'TU_KEY\', version=3.5); d.set_socketPersistent(False); print(d.set_status(True, 20))"'),
      spacer(),
      new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: "Apagar el foco:", font: "Arial", size: 26, bold: true, color: "2E75B6" })], spacing: { before: 240, after: 120 } }),
      code('py -c "import tinytuya; d = tinytuya.BulbDevice(\'ebe997370c6c715b97qsgw\', \'TU_IP\', \'TU_KEY\', version=3.5); d.set_socketPersistent(False); print(d.set_status(False, 20))"'),
      spacer(),
      infoBox("En PowerShell, si la Local Key tiene el simbolo $, agregale un backtick (`) antes de cada $. Ejemplo: jU2w`$ER0nHBIPS."),
      spacer(),
      divider(),

      // SOLUCION DE PROBLEMAS
      new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: "Solucion de Problemas Comunes", font: "Arial", size: 32, bold: true })], spacing: { before: 360, after: 180 } }),
      spacer(),
      new Table({
        width: { size: 9360, type: WidthType.DXA },
        columnWidths: [4000, 5360],
        rows: [
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 4000, type: WidthType.DXA }, shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Error / Problema", font: "Arial", size: 22, bold: true })] })] }),
              new TableCell({ borders, width: { size: 5360, type: WidthType.DXA }, shading: { fill: "D5E8F0", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Solucion", font: "Arial", size: 22, bold: true })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 4000, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Foco dice SIN CONEXION", font: "Arial", size: 22 })] })] }),
              new TableCell({ borders, width: { size: 5360, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Verificar IP en .env y que laptop este en la misma red WiFi que el foco", font: "Arial", size: 22 })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 4000, type: WidthType.DXA }, shading: { fill: "F9F9F9", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Error 914: Check device key or version", font: "Courier New", size: 20 })] })] }),
              new TableCell({ borders, width: { size: 5360, type: WidthType.DXA }, shading: { fill: "F9F9F9", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Local Key incorrecta. Repetir Paso 3 para obtener la nueva key", font: "Arial", size: 22 })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 4000, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "No se encontro Python", font: "Arial", size: 22 })] })] }),
              new TableCell({ borders, width: { size: 5360, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Usar py en lugar de python en todos los comandos", font: "Arial", size: 22 })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 4000, type: WidthType.DXA }, shading: { fill: "F9F9F9", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Foco no aparece en SmartLife al agregar", font: "Arial", size: 22 })] })] }),
              new TableCell({ borders, width: { size: 5360, type: WidthType.DXA }, shading: { fill: "F9F9F9", type: ShadingType.CLEAR }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "Verificar que el WiFi es 2.4 GHz. Reiniciar el foco desenchufandolo 10 segundos", font: "Arial", size: 22 })] })] }),
            ]
          }),
          new TableRow({
            children: [
              new TableCell({ borders, width: { size: 4000, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "El foco no cambia de estado con los comandos", font: "Arial", size: 22 })] })] }),
              new TableCell({ borders, width: { size: 5360, type: WidthType.DXA }, margins: { top: 80, bottom: 80, left: 120, right: 120 }, children: [new Paragraph({ children: [new TextRun({ text: "El backend puede tener el socket ocupado. Detener server.py antes de usar comandos directos", font: "Arial", size: 22 })] })] }),
            ]
          }),
        ]
      }),
      spacer(),
    ]
  }]
});

Packer.toBuffer(doc).then(buffer => {
  fs.writeFileSync("C:\\Users\\andre\\HELEN-v5.0\\Helen-Web\\Guia-Foco-RGB.docx", buffer);
  console.log("Documento creado: Guia-Foco-RGB.docx");
});
