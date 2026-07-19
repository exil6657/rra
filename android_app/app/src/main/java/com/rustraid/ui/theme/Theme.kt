package com.rustraid.ui.theme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
@Composable fun RustRaidTheme(amoledBlack:Boolean=false,content:@Composable()->Unit){
 val colors=darkColorScheme(primary=Green,secondary=Blue,tertiary=Orange,background=if(amoledBlack)Color.Black else Black,surface=if(amoledBlack)Color.Black else Card,error=Red)
 MaterialTheme(colorScheme=colors,typography=Typography(),content=content)
}
