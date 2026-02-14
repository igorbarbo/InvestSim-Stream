# services/analise_service.py
from services.preco_service import DadosAtivo

class AnaliseResultado:
    """Resultado estruturado da análise de preço."""
    
    def __init__(self, status: str, mensagem: str, cor: str, explicacao: str,
                 pontuacao: int, recomendacao: str, preco_ideal_compra: float,
                 preco_teto: float):
        self.status = status
        self.mensagem = mensagem
        self.cor = cor
        self.explicacao = explicacao
        self.pontuacao = pontuacao
        self.recomendacao = recomendacao
        self.preco_ideal_compra = preco_ideal_compra
        self.preco_teto = preco_teto


class AnaliseService:
    """Serviço de análise técnica (caro/barato)."""
    
    # Thresholds e cores
    THRESHOLDS = {
        'oportunidade': -40,
        'barato': -20,
        'neutro': 0,
        'atencao': 20,
        'caro': float('inf')
    }
    
    CORES = {
        'oportunidade': '#00FF00',
        'barato': '#90EE90',
        'neutro': '#D4AF37',
        'atencao': '#FFA500',
        'caro': '#FF4444'
    }
    
    def analisar(self, dados: DadosAtivo) -> AnaliseResultado:
        """Executa análise completa baseada em dados históricos."""
        
        if dados.status != "ok":
            return AnaliseResultado(
                status="neutro",
                mensagem="🔵 DADOS INSUFICIENTES",
                cor="#808080",
                explicacao="Não há dados históricos suficientes para análise.",
                pontuacao=0,
                recomendacao="Aguardar",
                preco_ideal_compra=0,
                preco_teto=0
            )
        
        p = dados.preco_atual
        m12 = dados.preco_medio_12m
        p20 = dados.percentil_20
        p80 = dados.percentil_80
        min5 = dados.minimo_5y
        max5 = dados.maximo_5y
        var_ano = dados.variacao_anual
        dy = dados.dividend_yield
        
        # Posição relativa
        pos_rel = ((p - min5) / (max5 - min5)) * 100 if max5 > min5 else 50
        
        pontuacao = 0
        motivos = []
        alerta_risco = ""
        
        # Comparação com média 12 meses
        if p < m12 * 0.85:
            pontuacao -= 25
            motivos.append("📉 Preço 15% abaixo da média de 12 meses")
        elif p < m12 * 0.9:
            pontuacao -= 20
            motivos.append("📉 Preço 10% abaixo da média de 12 meses")
        elif p < m12:
            pontuacao -= 10
            motivos.append("📉 Preço abaixo da média de 12 meses")
        elif p > m12 * 1.15:
            pontuacao += 25
            motivos.append("📈 Preço 15% acima da média de 12 meses")
        elif p > m12 * 1.1:
            pontuacao += 20
            motivos.append("📈 Preço 10% acima da média de 12 meses")
        elif p > m12:
            pontuacao += 10
            motivos.append("📈 Preço acima da média de 12 meses")
        
        # Percentis
        if p < p20:
            pontuacao -= 30
            motivos.append("💰 Entre os 20% preços mais baixos dos últimos 5 anos")
        elif p > p80:
            pontuacao += 30
            motivos.append("⚠️ Entre os 20% preços mais altos dos últimos 5 anos")
        
        # Posição na faixa
        if pos_rel < 15:
            pontuacao -= 25
            motivos.append(f"🎯 Próximo da mínima histórica (R$ {min5:.2f})")
        elif pos_rel < 30:
            pontuacao -= 15
            motivos.append("📊 Na faixa inferior da série histórica")
        elif pos_rel > 85:
            pontuacao += 25
            motivos.append(f"🔴 Próximo da máxima histórica (R$ {max5:.2f})")
        elif pos_rel > 70:
            pontuacao += 15
            motivos.append("📊 Na faixa superior da série histórica")
        
        # Variação anual
        if var_ano < -20:
            pontuacao -= 20
            motivos.append(f"📉 Caiu {var_ano:.1f}% no último ano")
            if var_ano < -50:
                alerta_risco = "\n\n⚠️ **ALERTA DE RISCO:** Queda superior a 50% no último ano. Verifique problemas fundamentais antes de investir."
        elif var_ano < -10:
            pontuacao -= 10
            motivos.append(f"📉 Caiu {var_ano:.1f}% no último ano")
        elif var_ano > 50:
            pontuacao += 25
            motivos.append(f"🚀 Subiu {var_ano:.1f}% no último ano")
        elif var_ano > 30:
            pontuacao += 15
            motivos.append(f"🚀 Subiu {var_ano:.1f}% no último ano")
        
        # Determinar status
        status = "caro"
        if pontuacao <= self.THRESHOLDS['oportunidade']:
            status = "oportunidade"
        elif pontuacao <= self.THRESHOLDS['barato']:
            status = "barato"
        elif pontuacao <= self.THRESHOLDS['neutro']:
            status = "neutro"
        elif pontuacao <= self.THRESHOLDS['atencao']:
            status = "atencao"
        
        # Construir explicação e mensagem
        if status == "oportunidade":
            mensagem = "🔥 OPORTUNIDADE! Muito barato"
            cor = self.CORES['oportunidade']
            explicacao = "### ✅ OPORTUNIDADE DE COMPRA!\n\n"
            explicacao += "**Este ativo está muito barato comparado à sua história:**\n\n"
            for m in motivos[:4]:
                explicacao += f"• {m}\n"
            explicacao += f"\n📊 **Preço atual:** R$ {p:.2f}\n"
            explicacao += f"📊 **Média 12m:** R$ {m12:.2f}\n"
            explicacao += f"📊 **Mínima 5 anos:** R$ {min5:.2f}\n"
            explicacao += f"📊 **Máxima 5 anos:** R$ {max5:.2f}\n"
            if dy:
                explicacao += f"💰 **Dividend Yield:** {dy:.2f}%\n"
            explicacao += f"\n💡 **RECOMENDAÇÃO:** COMPRAR - Ótimo ponto de entrada!" + alerta_risco
            preco_ideal = p
        elif status == "barato":
            mensagem = "👍 Barato - Bom momento"
            cor = self.CORES['barato']
            explicacao = "### ✅ PREÇO ATRATIVO\n\n"
            explicacao += "**Este ativo está abaixo da média histórica:**\n\n"
            for m in motivos[:3]:
                explicacao += f"• {m}\n"
            explicacao += f"\n📊 **Preço atual:** R$ {p:.2f}\n"
            explicacao += f"📊 **Média 12m:** R$ {m12:.2f}\n"
            if dy:
                explicacao += f"💰 **Dividend Yield:** {dy:.2f}%\n"
            explicacao += f"\n💡 **RECOMENDAÇÃO:** Pode comprar - preço justo" + alerta_risco
            preco_ideal = p
        elif status == "neutro":
            mensagem = "⚖️ Preço justo"
            cor = self.CORES['neutro']
            explicacao = "### ⚖️ PREÇO JUSTO\n\n"
            explicacao += "**Este ativo está dentro da faixa histórica normal:**\n\n"
            for m in motivos[:2]:
                explicacao += f"• {m}\n"
            explicacao += f"\n📊 **Preço atual:** R$ {p:.2f}\n"
            explicacao += f"📊 **Média 12m:** R$ {m12:.2f}\n"
            explicacao += f"\n💡 **RECOMENDAÇÃO:** Compra neutra - nem barato nem caro" + alerta_risco
            preco_ideal = p
        elif status == "atencao":
            mensagem = "⚠️ Atenção - Acima da média"
            cor = self.CORES['atencao']
            preco_ideal = m12 * 0.9
            explicacao = "### ⚠️ PREÇO ELEVADO\n\n"
            explicacao += "**Este ativo está acima da média histórica:**\n\n"
            for m in motivos[:3]:
                explicacao += f"• {m}\n"
            explicacao += f"\n📊 **Preço atual:** R$ {p:.2f}\n"
            explicacao += f"📊 **Média 12m:** R$ {m12:.2f}\n"
            explicacao += f"📊 **Máxima 5 anos:** R$ {max5:.2f}\n"
            explicacao += f"\n💡 **RECOMENDAÇÃO:** Comprar só se necessário - preço salgado" + alerta_risco
        else:  # caro
            mensagem = "❌ CARO! Evite comprar"
            cor = self.CORES['caro']
            preco_ideal = m12 * 0.9
            explicacao = "### ❌ PREÇO CARO DEMAIS!\n\n"
            explicacao += "**Este ativo está muito caro comparado à sua história:**\n\n"
            for m in motivos[:4]:
                explicacao += f"• {m}\n"
            explicacao += f"\n📊 **Preço atual:** R$ {p:.2f}\n"
            explicacao += f"📊 **Média 12m:** R$ {m12:.2f}\n"
            explicacao += f"📊 **Máxima 5 anos:** R$ {max5:.2f}\n"
            if dy:
                explicacao += f"💰 **Dividend Yield:** {dy:.2f}%\n"
            explicacao += f"\n💡 **RECOMENDAÇÃO:** NÃO COMPRAR AGORA!\n   Espere o preço cair para pelo menos R$ {preco_ideal:.2f}" + alerta_risco
        
        # Preço teto aproximado
        preco_teto = (dy * p) / 6 if dy else 0
        
        return AnaliseResultado(
            status=status,
            mensagem=mensagem,
            cor=cor,
            explicacao=explicacao,
            pontuacao=pontuacao,
            recomendacao="COMPRAR" if status in ["oportunidade", "barato"] else "ESPERAR",
            preco_ideal_compra=preco_ideal,
            preco_teto=preco_teto
        )
