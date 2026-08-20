import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

void Promise.all([
  loadFont({family: 'Noto Sans Thai', url: staticFile('NotoSansThai-Variable.ttf'), weight: '400'}),
  loadFont({family: 'Noto Sans Thai', url: staticFile('NotoSansThai-Variable.ttf'), weight: '700'}),
  loadFont({family: 'Noto Sans Thai', url: staticFile('NotoSansThai-Variable.ttf'), weight: '800'}),
]);
