import {create} from "zustand";
type State={indicator:string;period:string;level:number;selected:string|null;comparisons:string[];basemap:string;set:(patch:Partial<State>)=>void};
export const useAtlas=create<State>((set)=>({indicator:"population",period:"2024",level:1,selected:null,comparisons:[],basemap:"osm",set}));
