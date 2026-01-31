from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_GET
from django.views.decorators.cache import never_cache

from certificados.models import Cliente

@require_GET
@never_cache
def aluno_por_cpf(request):
    cpf = (request.GET.get("cpf") or "").strip()
    cpf_digits = "".join(ch for ch in cpf if ch.isdigit())

    aluno = Cliente.objects.filter(cpf=cpf_digits).first()
    if not aluno:
        return JsonResponse({"detail": "not found"}, status=404)

    # ⚠️ LGPD: renvoyer uniquement ce qui est nécessaire au pré-remplissage
    return JsonResponse({
        "nome": aluno.nome,
        "email": aluno.email,
        "telefone": aluno.telefone,
        "data_nascimento": aluno.data_nascimento.strftime("%Y-%m-%d") if aluno.data_nascimento else "",
        "endereco": aluno.endereco,
    })
