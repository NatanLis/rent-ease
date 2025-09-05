import colors from 'tailwindcss/colors';
import type { Config } from 'tailwindcss';

export default <Partial<Config>>{
  safelist: [ ...(Object.keys(colors)).map(c => `bg-${c}-400`) ],
  theme: {
    // extend: {
    //   fontFamily: {
    //     sans: ['Montserrat', 'ui-sans-serif', 'system-ui', 'sans-serif'],
    //     logo: ['Outfit', 'ui-sans-serif', 'system-ui', 'sans-serif'],
    //   }
    // }
  }
}
