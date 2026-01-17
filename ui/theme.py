import flet as ft

class ThemeColors:
    # 2026 Modern Palette (Violet-Blue Future)
    PRIMARY = "#7C3AED"  # Violet
    PRIMARY_LIGHT = "#A78BFA"
    SECONDARY = "#2563EB"  # Blue
    ACCENT = "#F43F5E"    # Rose/Pink for attention
    
    BG_DARK = "#050505"
    BG_CARD = "#121212"
    
    GLASS_BG = "0x20FFFFFF"
    GLASS_BORDER = "0x30FFFFFF"
    
    TEXT_MAIN = "#FFFFFF"
    TEXT_DIM = "#9CA3AF"

class DesignSystem:
    GRADIENT_PRIMARY = ft.LinearGradient(
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
        colors=[ThemeColors.PRIMARY, ThemeColors.SECONDARY],
    )
    
    GRADIENT_GLASS = ft.LinearGradient(
        begin=ft.alignment.top_left,
        end=ft.alignment.bottom_right,
        colors=[ft.Colors.with_opacity(0.1, ft.Colors.WHITE), ft.Colors.with_opacity(0.05, ft.Colors.WHITE)],
    )
    
    SHADOW_GLOW = ft.BoxShadow(
        blur_radius=20,
        color=ft.Colors.with_opacity(0.3, ThemeColors.PRIMARY),
        spread_radius=-5,
    )
    
    BORDER_RADIUS = 20
    BORDER_WIDTH = 1.5

def get_theme_mode():
    return ft.ThemeMode.DARK
