from fpdf import FPDF
import datetime

class PrivatePDF(FPDF):
    def header(self):
        self.set_fill_color(10, 20, 35) 
        self.rect(0, 0, 210, 45, 'F')
        self.set_font('Times', 'B', 22)
        self.set_text_color(212, 175, 55)
        self.cell(0, 25, 'IGORBARBO PRIVATE WEALTH', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        data = datetime.datetime.now().strftime("%d/%m/%Y")
        self.cell(0, 10, f'Relatório Estratégico - Gerado em {data}', 0, 0, 'C')

def generate(df, total_brl, mwa):
    pdf = PrivatePDF()
    pdf.add_page()
    pdf.set_font("Times", 'B', 14)
    pdf.cell(0, 10, f"Patrimonio Consolidado: R$ {total_brl:,.2f}", ln=True)
    pdf.ln(5)
    
    pdf.set_fill_color(245, 245, 245)
    pdf.cell(90, 10, ' ATIVO', 0, 0, 'L', 1)
    pdf.cell(90, 10, 'VALOR ATUALIZADO ', 0, 1, 'R', 1)
    
    pdf.set_font("Times", size=11)
    for _, row in df.iterrows():
        patr = row.get('Patrimônio', 0)
        pdf.cell(90, 10, f" {row['ticker']}", border='B')
        pdf.cell(90, 10, f"R$ {patr:,.2f} ", border='B', ln=1, align='R')
    
    pdf.ln(20)
    pdf.set_font('Times', 'I', 9)
    pdf.multi_cell(0, 5, "Estratégia Híbrida 10% a.a. | Aporte Mensal R$ 3.000,00 | Reinvestimento Total.")
    return pdf.output(dest='S').encode('latin-1')
    
