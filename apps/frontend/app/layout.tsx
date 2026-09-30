import "maplibre-gl/dist/maplibre-gl.css";
import "./styles.css";
import "./extra.css";
import Providers from "@/components/Providers";
export const metadata={title:"Qazaqstan Atlas",description:"Интерактивный статистический атлас Казахстана"};
export default function Layout({children}:{children:React.ReactNode}){return <html lang="ru"><body><Providers>{children}</Providers></body></html>}
