import numpy as np
import matplotlib.pyplot as plt

# 1. parametros

impedancia_carga = 6.0     # 6 Ohms
frequencia_corte = 2800.0  # 2.8 kHz


# 2. tabelas

tabela_capacitores_uf = np.array([
    1.0, 1.2, 1.5, 1.8, 2.2, 2.7,
    3.3, 3.9, 4.7, 5.6, 6.8, 8.2,
    10.0, 12.0, 15.0, 18.0, 22.0, 27.0,
    33.0, 39.0, 47.0, 56.0, 68.0, 82.0,
    100.0
])

tabela_indutores_mh = np.array([
    0.10, 0.12, 0.15, 0.18, 0.22, 0.27,
    0.33, 0.39, 0.47, 0.56, 0.68, 0.82,
    1.0, 1.2, 1.5, 1.8, 2.2, 2.7,
    3.3, 3.9, 4.7, 5.6, 6.8, 8.2,
    10.0, 12.0, 15.0
])

# contas

#divisao de corrente
def parallel(z1, z2):
    return (z1 * z2) / (z1 + z2)

#função que seleciona qual valor da tabela pegar
def find_nearest(value, standards):
    array = np.asarray(standards)
    idx = (np.abs(array - value)).argmin()
    nearest = array[idx]
    error = ((nearest - value) / value) * 100
    return nearest, error

Z = impedancia_carga
fc = frequencia_corte
omega_c = 2 * np.pi * fc

# contas p encontrar o indutor e cpaacitor 
# Woofer 
L_lp_ideal = (1.4142 * Z) / omega_c
C_lp_ideal = 1.4142 / (omega_c * Z)

# Tweeter 
C_hp_ideal = 1.0 / (1.4142 * Z * omega_c)
L_hp_ideal = Z / (1.4142 * omega_c)

# seleção a partir das tabelas
L_lp_real_mh, L_lp_err = find_nearest(L_lp_ideal * 1000, tabela_indutores_mh)
C_lp_real_uf, C_lp_err = find_nearest(C_lp_ideal * 1e6, tabela_capacitores_uf)

L_hp_real_mh, L_hp_err = find_nearest(L_hp_ideal * 1000, tabela_indutores_mh)
C_hp_real_uf, C_hp_err = find_nearest(C_hp_ideal * 1e6, tabela_capacitores_uf)


print(f"=== PROJETO CROSSOVER (Z={Z} Ohms | fc={fc} Hz) ===")
print("=" * 60)

print(f"\n[WOOFER - passa baixa]")
print(f"  Indutor (L):    Ideal: {L_lp_ideal*1000:.3f} mH  -> USAR: {L_lp_real_mh} mH (Erro: {L_lp_err:.1f}%)")
print(f"  Capacitor (C): Ideal: {C_lp_ideal*1e6:.3f} uF   -> USAR: {C_lp_real_uf} uF (Erro: {C_lp_err:.1f}%)")

print(f"\n[TWEETER - passa alta]")
print(f"  Capacitor (C): Ideal: {C_hp_ideal*1e6:.3f} uF   -> USAR: {C_hp_real_uf} uF (Erro: {C_hp_err:.1f}%)")
print(f"  Indutor (L):    Ideal: {L_hp_ideal*1000:.3f} mH  -> USAR: {L_hp_real_mh} mH (Erro: {L_hp_err:.1f}%)")

# 5. grafico IDEAL vs REAL
# convertendo os componentes (Henries e Farads) em impedâncias (Ohms) para calcular como o som se comporta em cada frequência.
freqs = np.logspace(2, 4.3, 1000) # 100Hz a 20kHz
w = 2 * np.pi * freqs

# >> WOOFER - indutor em série, capacitor em paralelo

# 1. Z_L (indutor): fórmula j*w*L.
# a impedância SOBE junto com a frequência, o indutor bloqueia os agudos.
Z_L_lp_i = 1j * w * L_lp_ideal
# 2. Z_C (capacitor): Fórmula 1/(j*w*C).
# a impedância DESCE quando a frequência sobe, o capacitor rouba os agudos.
Z_C_lp_i = 1 / (1j * w * C_lp_ideal)
# 3. divisor de tensão.
# calcula quanto sinal sobra para o falante (Z) depois de passar pelo filtro.
# lógica: (impedância em paralelo) / (impedância total do circuito)
H_lp_ideal = parallel(Z_C_lp_i, Z) / (parallel(Z_C_lp_i, Z) + Z_L_lp_i)

# >> TWEETER - capacitor em série, indutor em paralelo

# 1. componentes invertidos: o capacitor agora bloqueia graves (série) e indutor limpa (paralelo).
Z_L_hp_i = 1j * w * L_hp_ideal
Z_C_hp_i = 1 / (1j * w * C_hp_ideal)
# 2. sinal útil fica sobre o indutor (que está em paralelo com o tweeter).
H_hp_ideal = parallel(Z_L_hp_i, Z) / (parallel(Z_L_hp_i, Z) + Z_C_hp_i)

#curvas REAIS (valores comerciais da tabela)
Z_L_lp_r = 1j * w * (L_lp_real_mh/1000)
Z_C_lp_r = 1 / (1j * w * (C_lp_real_uf/1e6))
H_lp_real = parallel(Z_C_lp_r, Z) / (parallel(Z_C_lp_r, Z) + Z_L_lp_r)

Z_L_hp_r = 1j * w * (L_hp_real_mh/1000)
Z_C_hp_r = 1 / (1j * w * (C_hp_real_uf/1e6))
H_hp_real = parallel(Z_L_hp_r, Z) / (parallel(Z_L_hp_r, Z) + Z_C_hp_r)

#plotagem
plt.figure(figsize=(12, 7))

# plot woofer
plt.semilogx(freqs, 20*np.log10(np.abs(H_lp_ideal)), 'b--', label='Woofer Ideal', alpha=0.5)
plt.semilogx(freqs, 20*np.log10(np.abs(H_lp_real)), 'b-', label='Woofer Real', linewidth=2)

# plot tweeter
plt.semilogx(freqs, 20*np.log10(np.abs(H_hp_ideal)), 'r--', label='Tweeter Ideal', alpha=0.5)
plt.semilogx(freqs, 20*np.log10(np.abs(H_hp_real)), 'r-', label='Tweeter Real', linewidth=2)

#detalhes d grafico
plt.axvline(x=fc, color='k', linestyle=':', label=f'Corte {int(fc)}Hz')
plt.axhline(y=-3, color='gray', linestyle=':', label='-3dB')

plt.title(f"Comparativo: Ideal vs Comercial (Z={Z}$\\Omega$, fc={int(fc)}Hz)")
plt.xlabel("Frequência (Hz)")
plt.ylabel("Magnitude (dB)")
plt.ylim(-50, 5)
plt.grid(True, which="both", alpha=0.3)
plt.legend()
plt.tight_layout()
plt.show()
