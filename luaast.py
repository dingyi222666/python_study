from luaparser import ast,astnodes,utils
from luaparser.utils.visitor import visitor


def main():
    source="""
        print("a print")
        for a,v in get(a) do
           while true do
           end
        end
        if a then else end
        switch a do
           case a:
           print("switch")
        end
    """
    out = ast.parse(
       source)
    DefaultVisitor().visit(out)


class DefaultVisitor(ast.ASTVisitor):
    def visit_Block(self, root:ast.Block):
        print(root)




if __name__ == '__main__':
    main()
