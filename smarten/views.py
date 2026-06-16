import subprocess, json, re
from django.http import JsonResponse
from rest_framework.decorators import api_view

@api_view(['POST', 'GET'])
def NetworkDiscovery(request):
     try:
          ipAddress = json.loads(request.body)["ip"]
          subnet = json.loads(request.body)["subnet"]

          if not ipAddress or not subnet:
               return JsonResponse({ "response": "Missing Ip address or subnet" })

          pattern = r"(?i)^\d{1,3}\.?\d{1,3}\.?\d{1,3}\.?\d{1,3}$"
          if not re.match(pattern, ipAddress):
               return JsonResponse({ "response": "Invalid IP address" })
          
          output = subprocess.check_output(["nmap", "-sn", f"{ipAddress}/{subnet}"])

          print(f"{output}")
          context = str(output)

          return JsonResponse({ "response": context })
     except Exception as e:
          print(e)
          return JsonResponse({ "response": str(e) })

@api_view(['POST', 'GET'])
def PortScanning(request):
     try:
          ipAddress = json.loads(request.body)["ip"]
          firstPorts = json.loads(request.body)["firstPorts"]

          if not ipAddress or not firstPorts:
               return JsonResponse({ "response": "Missing Ip address or subnet" })

          pattern = r"(?i)^\d{1,3}\.?\d{1,3}\.?\d{1,3}\.?\d{1,3}$"
          if not re.match(pattern, ipAddress):
               return JsonResponse({ "response": "Invalid IP address" })
          
          output = subprocess.check_output(["nmap", "-F" if firstPorts == 'yes' else "", ipAddress])

          # print(f"{output}")
          context = str(output)

          return JsonResponse({ "response": context })
     except Exception as e:
          print(e)
          return JsonResponse({ "response": str(e) })