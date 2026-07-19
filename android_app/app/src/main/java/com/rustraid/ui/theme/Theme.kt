package com.rustraid.ui.theme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
private val colors=darkColorScheme(primary=Green,secondary=Blue,tertiary=Orange,background=Black,surface=Card,error=Red)
@Composable fun RustRaidTheme(content:@Composable()->Unit)=MaterialTheme(colorScheme=colors,typography=Typography(),content=content)
