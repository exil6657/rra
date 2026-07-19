package com.rustraid.ui.theme
import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val RustTypography = Typography(
    headlineLarge = TextStyle(fontFamily=FontFamily.SansSerif,fontWeight=FontWeight.Black,fontSize=30.sp,letterSpacing=(-1).sp),
    headlineMedium = TextStyle(fontFamily=FontFamily.SansSerif,fontWeight=FontWeight.ExtraBold,fontSize=24.sp,letterSpacing=(-0.5).sp),
    headlineSmall = TextStyle(fontFamily=FontFamily.SansSerif,fontWeight=FontWeight.ExtraBold,fontSize=19.sp),
    titleMedium = TextStyle(fontFamily=FontFamily.SansSerif,fontWeight=FontWeight.Bold,fontSize=16.sp),
    bodyMedium = TextStyle(fontFamily=FontFamily.SansSerif,fontSize=14.sp,lineHeight=20.sp),
    labelLarge = TextStyle(fontFamily=FontFamily.Monospace,fontWeight=FontWeight.Bold,fontSize=12.sp,letterSpacing=0.8.sp),
    labelSmall = TextStyle(fontFamily=FontFamily.Monospace,fontSize=10.sp,letterSpacing=0.6.sp)
)
