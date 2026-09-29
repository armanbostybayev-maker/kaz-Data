"use client";
import {QueryClient,QueryClientProvider} from "@tanstack/react-query";
import {useState} from "react";
import Atlas from "@/components/Atlas";
export default function Page(){const [client]=useState(()=>new QueryClient());return <QueryClientProvider client={client}><Atlas/></QueryClientProvider>}

