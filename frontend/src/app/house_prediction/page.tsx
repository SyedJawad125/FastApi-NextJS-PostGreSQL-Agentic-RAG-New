'use client'
import React from 'react'
import AdminSideNavbarCom from "@/components/AdminSideNavbarCom";
import House_predictionCom from "@/components/House_predictionCom";


const page = () => {
  return (
    <div className="flex h-screen">
      <div className="w-[16%] bg-gray-800 text-white">
        <AdminSideNavbarCom />
      </div>
      <div className="w-[84%] p-6 bg-black">
      <House_predictionCom/> 
      </div>
    </div> 
  )
}

export default page
