from typing import Any
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.shortcuts import render
from django.views.generic import View
from visualizeTree.LearningDecisionTree import load_tree, pruneTree, Tree, analyze_mail

tree : Tree = load_tree()
tree = pruneTree(tree)

# Create your views here.
class IndexView(View):
    template_name = 'visualizeTree/index.html'
    def get(self, request: HttpRequest) -> HttpResponse:
        tree_dict = tree.to_dict()
        return render(request, self.template_name, {'tree_dict': tree_dict})