import { create } from "zustand";
type State = {indicator:string; year:number; level:number; selected:string|null; basemap:string; set:(patch:Partial<State>)=>void};
export const useAtlas = create<State>((set)=>({indicator:"population",year:2024,level:1,selected:null,basemap:"osm",set}));

