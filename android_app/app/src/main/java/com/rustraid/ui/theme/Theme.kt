package com.rustraid.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

@Composable
fun RustRaidTheme(amoledBlack: Boolean = false, content: @Composable () -> Unit) {
    val colors = darkColorScheme(
        primary = Purple,
        onPrimary = Color.White,
        primaryContainer = PurpleDeep,
        secondary = PurpleSoft,
        tertiary = Orange,
        background = if (amoledBlack) Color.Black else Black,
        surface = if (amoledBlack) Color.Black else Card,
        surfaceVariant = Field,
        outline = Border,
        error = Red,
        onBackground = TextPrimary,
        onSurface = TextPrimary
    )
    MaterialTheme(colorScheme = colors, typography = RustTypography, content = content)
}
