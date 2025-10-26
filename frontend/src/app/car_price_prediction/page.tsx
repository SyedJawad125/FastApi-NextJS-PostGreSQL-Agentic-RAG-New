'use client'
import React from 'react'
import AdminSideNavbarCom from "@/components/AdminSideNavbarCom";
import Car_Price_Prediction from "@/components/Car_Price_Prediction";


const page = () => {
  return (
    <div className="flex h-screen">
      <div className="w-[16%] bg-gray-800 text-white">
        <AdminSideNavbarCom />
      </div>
      <div className="w-[84%] p-6 bg-black">
      <Car_Price_Prediction/> 
      </div>
    </div> 
  )
}

export default page
