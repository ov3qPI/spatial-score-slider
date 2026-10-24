package cc0.KPYQrT.spatialscoreslider;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.graphics.Color;
import android.graphics.PorterDuff;
import android.graphics.drawable.Drawable;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.SeekBar;
import android.widget.TextView;
import android.widget.Toast;
public class MainActivity extends Activity {
private static final String SOURCE_ID="SpatialScoreSlider_MainActivity_v20261024T050357Z";
private static final int DEFAULT_MAX=100;
private static final String PLACEHOLDER="—";
private static final int BACKGROUND_COLOR=Color.rgb(35,32,29);
private static final int START_COLOR=Color.parseColor("#D68A3A");
private static final int END_COLOR=Color.parseColor("#4C7EA8");
private SeekBar slider;
private TextView scoreValue;
private TextView maxValue;
private Button resetButton;
private FrameLayout screenRoot;
private View sliderGroup;
private View scoreOutput;
private boolean revealed=false;
@Override protected void onCreate(Bundle savedInstanceState) {
super.onCreate(savedInstanceState);
Window window=getWindow();
window.addFlags(WindowManager.LayoutParams.FLAG_DRAWS_SYSTEM_BAR_BACKGROUNDS);
window.clearFlags(WindowManager.LayoutParams.FLAG_TRANSLUCENT_STATUS|WindowManager.LayoutParams.FLAG_TRANSLUCENT_NAVIGATION);
window.setStatusBarColor(BACKGROUND_COLOR);
window.setNavigationBarColor(BACKGROUND_COLOR);
View decor=window.getDecorView();
decor.setSystemUiVisibility(decor.getSystemUiVisibility()&~(View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR|View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR));
setContentView(R.layout.activity_main);
screenRoot=findViewById(R.id.screenRoot);
sliderGroup=findViewById(R.id.sliderGroup);
scoreOutput=findViewById(R.id.scoreOutput);
slider=findViewById(R.id.slider);
scoreValue=findViewById(R.id.scoreValue);
maxValue=findViewById(R.id.maxValue);
resetButton=findViewById(R.id.resetButton);
slider.setMax(DEFAULT_MAX);
maxValue.setText(String.valueOf(DEFAULT_MAX));
screenRoot.addOnLayoutChangeListener((v,left,top,right,bottom,oldLeft,oldTop,oldRight,oldBottom)->positionAtScreenCenterline());
slider.setOnSeekBarChangeListener(new SeekBar.OnSeekBarChangeListener() {
@Override public void onProgressChanged(SeekBar seekBar,int progress,boolean fromUser) {
updateSliderColor(progress);
if(!revealed) scoreValue.setText(PLACEHOLDER);
}
@Override public void onStartTrackingTouch(SeekBar seekBar) {
revealed=false;
scoreValue.setText(PLACEHOLDER);
}
@Override public void onStopTrackingTouch(SeekBar seekBar) {
revealed=true;
scoreValue.setText(String.valueOf(slider.getProgress()));
}
});
resetButton.setOnClickListener(v->resetScore());
scoreValue.setOnClickListener(v->{
if(!revealed) return;
String value=scoreValue.getText().toString();
ClipboardManager clipboard=(ClipboardManager)getSystemService(CLIPBOARD_SERVICE);
clipboard.setPrimaryClip(ClipData.newPlainText(getString(R.string.app_name),value));
Toast.makeText(this,"Copied: "+value,Toast.LENGTH_SHORT).show();
});
updateSliderColor(0);
}
private int dp(float value) {
return Math.round(value*getResources().getDisplayMetrics().density);
}
private void positionAtScreenCenterline() {
if(screenRoot.getHeight()==0||slider.getHeight()==0||scoreOutput.getHeight()==0) return;
int centerline=screenRoot.getHeight()/2;
int sliderCenterWithinGroup=slider.getTop()+slider.getHeight()/2;
int sliderTop=centerline-sliderCenterWithinGroup-screenRoot.getPaddingTop();
FrameLayout.LayoutParams sliderParams=(FrameLayout.LayoutParams)sliderGroup.getLayoutParams();
if(sliderParams.topMargin!=sliderTop) {
sliderParams.topMargin=sliderTop;
sliderGroup.setLayoutParams(sliderParams);
}
int outputBottom=centerline-slider.getHeight()/2-dp(24);
int outputTop=outputBottom-scoreOutput.getHeight()-screenRoot.getPaddingTop();
FrameLayout.LayoutParams outputParams=(FrameLayout.LayoutParams)scoreOutput.getLayoutParams();
if(outputParams.topMargin!=outputTop) {
outputParams.topMargin=outputTop;
scoreOutput.setLayoutParams(outputParams);
}
}
private void resetScore() {
slider.setProgress(0);
revealed=false;
scoreValue.setText(PLACEHOLDER);
updateSliderColor(0);
}
private void updateSliderColor(int progress) {
float t=(float)progress/DEFAULT_MAX;
int r=(int)(Color.red(START_COLOR)+(Color.red(END_COLOR)-Color.red(START_COLOR))*t);
int g=(int)(Color.green(START_COLOR)+(Color.green(END_COLOR)-Color.green(START_COLOR))*t);
int b=(int)(Color.blue(START_COLOR)+(Color.blue(END_COLOR)-Color.blue(START_COLOR))*t);
Drawable drawable=slider.getProgressDrawable().mutate();
drawable.setColorFilter(Color.rgb(r,g,b),PorterDuff.Mode.SRC_IN);
}
}
